function addActivePlayers(peg_name, peg_colour, gender) {
  let jsonData = {
    'peg_name': peg_name,
    'peg_colour': peg_colour,
    'gender': gender
  }


  fetch('http://127.0.0.1:8000/projects/roundrobin/api/addactive/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')  // Required by Django
    },
    body: JSON.stringify(jsonData)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Response from backend:', data);

  })
  .catch(error => {
    console.error('Error sending array:', error);
  });

}

function removeActivePlayers(peg_name) {
  let jsonData = {
    'peg_name': peg_name
  }


  fetch('http://127.0.0.1:8000/projects/roundrobin/api/removeactive/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')  // Required by Django
    },
    body: JSON.stringify(jsonData)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Response from backend:', data);

  })
  .catch(error => {
    console.error('Error sending array:', error);
  });

}

document.getElementById('search-box').addEventListener('input', function () {
  document.getElementById("already-added").textContent = ""
  const query = this.value.trim();
  if (query.length < 2) {
    document.getElementById('results-list').innerHTML = '';
    return;
  }

  fetch(`http://127.0.0.1:8000/projects/roundrobin/api/players/?q=${encodeURIComponent(query)}`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json())
  .then(data => {
    const list = document.getElementById('results-list');
    list.innerHTML = '';

    if (data.length === 0) {
      list.innerHTML = '<li>No results found.</li>';
      return;
    }

    data.forEach(player => {
      const item = document.createElement('li');
      item.textContent = player.peg_name;
      item.id = player.id
      item.setAttribute("gender", player.gender)
      item.setAttribute("peg_colour", player.peg_colour)
      item.addEventListener("click", (e) => {
        let active = document.getElementById('active-players')
        for (let active_player of active.children) {
          if(active_player.textContent == item.textContent) {
            console.log("already active")
            document.getElementById("already-added").textContent = active_player.textContent + " is already in queue!"
            return
          }
        }
        //console.log(e.target.getAttribute('gender'))
        addActivePlayers(e.target.textContent, e.target.getAttribute('peg_colour'), e.target.getAttribute('gender'))
        document.getElementById("already-added").textContent = ""
        const element = document.createElement('li')
        element.textContent = item.textContent
        element.id = item.id
        element.addEventListener("click", (e) => {
          document.getElementById("already-added").textContent = e.target.textContent + " has been removed from the queue."
          removeActivePlayers(e.target.textContent)
          e.target.remove()
          //updateActivePlayers()
        })
        active.appendChild(element)
        //updateActivePlayers()
      })
      list.appendChild(item);
    });
  })
  .catch(error => {
    console.error('Search failed:', error);
  });
});

function saveSelectState() {
  const selectElement = document.getElementById('nCourts'); // Get the select element
  const selectedValue = selectElement.value; // Get the selected value
  document.cookie = `mySelectState=${selectedValue}; expires=Thu, 18 Dec 2026 12:00:00 UTC; path=/`; // Set the cookie
}

// Attach an event listener to the select element
document.getElementById('nCourts').addEventListener('change', saveSelectState);

function restoreActivePlayers() {
  fetch(`http://127.0.0.1:8000/projects/roundrobin/api/getactive/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json())
  .then(data => {
    //console.log(data.active_players.replace("[", "").replace("]", "").split(","))
    let jsonData = JSON.parse(data)
    for (const player of jsonData) {
      const list = document.getElementById('active-players')
      const element = document.createElement('li')
      element.textContent = player.peg_name
      // element.id = player.id
      element.setAttribute("gender", player.gender)
      element.setAttribute("peg_colour", player.peg_colour)
      element.addEventListener("click", (e) => {
        document.getElementById("already-added").textContent = e.target.textContent + " has been removed from the queue."
        removeActivePlayers(e.target.textContent)
        e.target.remove()
      })
      list.appendChild(element)
    }
  })
  .catch(error => {
    console.error('Search failed:', error);
  })
}

function restoreSelectState() {
  const cookies = document.cookie.split(';'); // Get all cookies and split them
  let selectState = null;

  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.startsWith('mySelectState=')) {
      selectState = cookie.substring('mySelectState='.length);
      break;
    }
  }

  if (selectState) {
    document.getElementById('nCourts').value = selectState; // Set the selected value
  }

  restoreActivePlayers()

  
}

function generateGame() {
  
  document.getElementById('games').textContent = "Loading..."
  document.getElementById('genGame').disabled = true

  fetch(`http://127.0.0.1:8000/projects/roundrobin/api/getnextgame/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json() )
  .then(data => {
    console.log(data)
    document.getElementById('games').textContent = JSON.stringify(data)
    document.getElementById('genGame').disabled = false

  })
  .catch(error => {
    console.error('Search failed:', error);
  })
}

function resetHistory() {

  fetch(`http://127.0.0.1:8000/projects/roundrobin/api/resetHistory/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .catch(error => {
    console.error('Error:', error);
  })

  document.getElementById('games').textContent = 'Game history successfully cleared.'
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

// function updateActivePlayers() {
//   let currently_active = document.getElementById('active-players').children
//   let id_array = []
//   for (const child of currently_active) {
//     id_array.push(parseInt(child.id))
//   }
//   const arrayAsString = JSON.stringify(id_array);  // e.g., "[1,2,3]"
//   console.log(arrayAsString)


//   fetch('http://127.0.0.1:8000/projects/roundrobin/api/active/', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'X-CSRFToken': getCookie('csrftoken')  // Required by Django
//     },
//     body: JSON.stringify({ data: arrayAsString })
//   })
//   .then(response => response.json())
//   .then(data => {
//     console.log('Response from backend:', data);

//   })
//   .catch(error => {
//     console.error('Error sending array:', error);
//   });

// }



// Call the function when the page loads
window.onload = restoreSelectState;

