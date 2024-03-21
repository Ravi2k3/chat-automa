/* 
Automa
Copyright (c) 2023, Automa
Unauthorized copying of this file, via any medium is strictly prohibited.
Proprietary and confidential.
*/

function validateAge(age) {
  if (age >= 18 && age <= 80) {
    return true;
  }
  return false;
}

function validateEmail(email) {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

function validateRequiredField(value) {
  return value && value.trim() !== "";
}

function navigateToSection(nextSectionId) {
  const currentSection = document.querySelector('.slide.show');
  const currentSectionId = currentSection.id;

  // Validation logic
  let canProceed = true;
  let errorMessage = "";

  if (currentSectionId === "section0") {
    const age = parseInt(document.querySelector('#age').value);
    const email = document.querySelector('#mail').value;
    const name = document.querySelector('#name').value;
    const nationality = document.querySelector('#nationality').value;

    if (!validateRequiredField(name)) {
      canProceed = false;
      errorMessage = "Name is required.";
    } else if (!validateRequiredField(nationality)) {
      canProceed = false;
      errorMessage = "Nationality is required.";
    } else if (!validateAge(age)) {
      canProceed = false;
      errorMessage = "Age must be between 18 and 80.";
    } else if (!validateEmail(email)) {
      canProceed = false;
      errorMessage = "Invalid email format.";
    }
  }

 // Show error message and return if can't proceed
if (!canProceed) {
  const flashMessage = document.createElement('div');
  flashMessage.className = 'flash-message';
  flashMessage.innerHTML = `<p>${errorMessage}</p>`;
  document.body.appendChild(flashMessage);

  // Show flash message
  setTimeout(() => {
    flashMessage.classList.add('show');
  }, 10);

  // Remove flash message after 3 seconds
  setTimeout(() => {
    flashMessage.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(flashMessage);
    }, 500);
  }, 3000);

  return;
}

  // Existing logic for navigating to the next section
  const sections = document.querySelectorAll('.slide');
  sections.forEach(section => {
    section.classList.remove('show');
    section.classList.add('hidden');
  });

  const nextSection = document.getElementById(nextSectionId);
  nextSection.classList.remove('hidden');

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      nextSection.classList.add('show');
    });
  });
}

function adjustHeight(textarea) {
    if(!textarea.classList.contains('single-line')) {
      textarea.style.height = (textarea.scrollHeight) + 'px';
    }
  }
 
  function dynamicMaxLength(textarea) {
    const style = window.getComputedStyle(textarea, null).getPropertyValue('font-size');
    const fontSize = parseFloat(style);
    const avgCharPx = fontSize * 0.6;
    const charsPerLine = Math.floor(textarea.clientWidth / avgCharPx);
    return charsPerLine * textarea.rows;
  }
  
document.addEventListener('DOMContentLoaded', function() {
    function adjustHeight(textarea) {
      textarea.style.height = (textarea.scrollHeight) + 'px';
    }
  
    const textareas = document.querySelectorAll('textarea');
    const inputs = document.querySelectorAll('textarea, input[type="button"]');
    const nextButton = document.querySelector('#next-button'); 
    
    textareas.forEach((textarea, index) => {
      // Update the maxLength dynamically when navigating sections or resizing the window
      let maxLength = dynamicMaxLength(textarea);
      window.addEventListener('resize', function() {
        maxLength = dynamicMaxLength(textarea);
      });
  
      function truncateText(text) {
        if (text.length > maxLength) {
          return text.substring(0, maxLength - 3) + '...';
        }
        return text;
      }
  
      textarea.addEventListener('input', function() {
        adjustHeight(this);
        maxLength = dynamicMaxLength(this);  // Update maxLength dynamically during input
        if (this.scrollHeight > this.clientHeight) {
          this.classList.remove('hide-scrollbar');
          this.classList.add('expanded');
        } else {
          this.classList.remove('expanded');
        }
      });
  
      textarea.addEventListener('blur', function() {
        this.style.height = '90px';
        this.classList.add('hide-scrollbar');
        this.classList.remove('expanded');
        this.setAttribute('data-original', this.value);  // Store full text
        
        // Dynamically get the corresponding hidden input ID based on the textarea's ID
        let fulltextId = this.id + '_fulltext';
        
        // Store the full text in the corresponding hidden input
        document.getElementById(fulltextId).value = this.value;
        
        // Set the textarea to the truncated text
        this.value = truncateText(this.value);
      });
    
      textarea.addEventListener('focus', function() {
        this.value = this.getAttribute('data-original') || this.value;  // Restore to full text
        adjustHeight(this);
        this.classList.remove('hide-scrollbar');
        this.classList.add('expanded');
      });
  
      textarea.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
          event.preventDefault();
          let nextIndex = index + 1;
          if (nextIndex < inputs.length) {
            inputs[nextIndex].focus();
          } else {
            this.blur(); 
          }
        }
      });
    });
  });


  document.addEventListener("DOMContentLoaded", function() {
    const section0Inputs = document.querySelectorAll("#section0 input, #section0 textarea");
    section0Inputs.forEach(function(input) {
      input.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
          event.preventDefault();
        }
      });
    });
  });

  document.addEventListener("DOMContentLoaded", function() {
    const clickableItems = document.querySelectorAll('.click');
    clickableItems.forEach(item => {
      item.addEventListener('click', function(event) {
        const anchor = item.querySelector('a');
        if (anchor && event.target !== anchor) {
          window.location.href = anchor.getAttribute('href');
        }
      });
    });
  });

  document.addEventListener('DOMContentLoaded', function() {
    const searchBar = document.getElementById('search-bar');
    const listItems = document.querySelectorAll('.list-item');

    searchBar.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();

        listItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query)) {
                item.parentElement.style.display = 'block';
            } else {
                item.parentElement.style.display = 'none';
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
  let allowCustomScroll = true;  
  let currentScroll = window.scrollY;
  let targetScroll = window.scrollY;
  let ease = 0.1;  // Smoothing factor

  function update() {
      if (allowCustomScroll) {  
          currentScroll += (targetScroll - currentScroll) * ease;
          if (Math.abs(targetScroll - currentScroll) > 0.1) {
              window.scrollTo(0, currentScroll);
          }
      }
      requestAnimationFrame(update);
  }

  function handleScroll(e) {
      if (allowCustomScroll) {  
          e.preventDefault();  
          targetScroll += e.deltaY;
          targetScroll = Math.min(Math.max(targetScroll, 0), document.body.scrollHeight - window.innerHeight);
      }
  }

  document.addEventListener("wheel", handleScroll, { passive: false });  
  requestAnimationFrame(update);
});