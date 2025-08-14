document.getElementById('search-box').addEventListener('input', function () {
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
          if(active_player.id == item.id) {
            console.log("already active")
            return
          }
        }
        const element = document.createElement('li')
        element.textContent = item.textContent
        element.id = item.id
        element.addEventListener("click", (e) => {
          e.target.remove()
          updateActivePlayers()
        })
        active.appendChild(element)
        updateActivePlayers()
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
  document.cookie = `mySelectState=${selectedValue}; expires=Thu, 18 Dec 2025 12:00:00 UTC; path=/`; // Set the cookie
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
    active_players_list = data.active_players.replace("[", "").replace("]", "").split(",")
    for (const player_id of active_players_list) {
      let pid = parseInt(player_id.replace(" ", ""))
      fetch(`http://127.0.0.1:8000/projects/roundrobin/api/player/?id=${encodeURIComponent(pid)}`, {
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
      })
      .then(res => res.json())
      .then(data => {
        //console.log(data.peg_name)
        const list = document.getElementById('active-players');
        const player = data
        const element = document.createElement('li')
        element.textContent = player.peg_name
        element.id = player.id
        element.setAttribute("gender", player.gender)
        element.setAttribute("peg_colour", player.peg_colour)
        element.addEventListener("click", (e) => {
          e.target.remove()
          updateActivePlayers()
        })
        list.appendChild(element)
      })
      .catch(error => {
        console.error('Search failed:', error);
      });
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

function updateActivePlayers() {
  let currently_active = document.getElementById('active-players').children
  let id_array = []
  for (const child of currently_active) {
    id_array.push(parseInt(child.id))
  }
  const arrayAsString = JSON.stringify(id_array);  // e.g., "[1,2,3]"
  console.log(arrayAsString)


  fetch('http://127.0.0.1:8000/projects/roundrobin/api/active/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')  // Required by Django
    },
    body: JSON.stringify({ data: arrayAsString })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Response from backend:', data);

  })
  .catch(error => {
    console.error('Error sending array:', error);
  });

}

// Call the function when the page loads
window.onload = restoreSelectState;

