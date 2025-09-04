function startRound() {
  let currentTime = new Date().getTime()
  fetch(origin + '/projects/roundrobin/api/settimer/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')  // Required by Django
    },
    body: JSON.stringify({'currentTime':currentTime})
  })
  .then(response => response.json())
  .then(data => {
    console.log('Response from backend:', data);
    if (data.res == 1) {
      console.log("current game is not over")
      document.getElementById('roundMessage').innerText = "Cannot start another round until the current round is over"
      return
    }
    loadTimer()
  })
  .catch(error => {
    console.error('Error sending array:', error);
  });
}

function addActivePlayers(peg_name, peg_colour, gender) {
  let jsonData = {
    'peg_name': peg_name,
    'peg_colour': peg_colour,
    'gender': gender
  }


  fetch(origin + '/projects/roundrobin/api/addactive/', {
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
    if (data.code == 0) {
      let active = document.getElementById('active-players')
      const element = document.createElement('li')
      element.textContent = peg_name
      element.setAttribute("gender", gender)
      element.setAttribute("peg_colour", peg_colour)
      element.addEventListener("click", (e) => {
        document.getElementById("already-added").textContent = e.target.textContent + " has been removed from the queue."
        removeActivePlayers(e.target.textContent)
        e.target.remove()
      })
      active.appendChild(element)
      document.getElementById("already-added").textContent = ""
    }
    else {
      document.getElementById("already-added").textContent = peg_name + " is already in the queue"
    }
  })
  .catch(error => {
    console.error('Error sending array:', error);
    document.getElementById("already-added").textContent = error
  });

}

function removeActivePlayers(peg_name) {
  let jsonData = {
    'peg_name': peg_name
  }


  fetch(origin + '/projects/roundrobin/api/removeactive/', {
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
    document.getElementById("already-added").textContent = peg_name + " has been removed from the queue."
  })
  .catch(error => {
    console.error('Error sending array:', error);
    document.getElementById("already-added").textContent = "failed to remove " + peg_name + " from the queue."
  });

}

document.getElementById('search-box').addEventListener('input', function () {
  document.getElementById("already-added").textContent = ""
  const query = this.value.trim();
  if (query.length < 2) {
    document.getElementById('results-list').innerHTML = '';
    return;
  }

  fetch(origin + `/projects/roundrobin/api/players/?q=${encodeURIComponent(query)}`, {
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
        addActivePlayers(e.target.textContent, e.target.getAttribute('peg_colour'), e.target.getAttribute('gender'))
      })
      list.appendChild(item);
    });
  })
  .catch(error => {
    console.error('Search failed:', error);
  });
});

function saveSelectState() {
  const courtsValue = document.getElementById('nCourts').value
  const minuteValue = document.getElementById('minutes').value // Get the select element

  fetch(origin + '/projects/roundrobin/api/setconfig/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')  // Required by Django
    },
    body: JSON.stringify({'nCourts':courtsValue, 'minutes':minuteValue})
  })
  .then(response => response.json())
  .then(data => {
    console.log('Response from backend:', data);
  })
  .catch(error => {
    console.error('Error sending array:', error);
  });
}

// Attach an event listener to the select element
document.getElementById('nCourts').addEventListener('change', saveSelectState);
document.getElementById('minutes').addEventListener('change', saveSelectState);


function restoreActivePlayers() {
  fetch(origin + `/projects/roundrobin/api/getactive/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json())
  .then(data => {
    let jsonData = JSON.parse(data)
    for (const player of jsonData) {
      const list = document.getElementById('active-players')
      const element = document.createElement('li')
      element.textContent = player.peg_name
      // element.id = player.id
      element.setAttribute("gender", player.gender)
      element.setAttribute("peg_colour", player.peg_colour)
      element.addEventListener("click", (e) => {
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

function restoreConfig() {
  fetch(origin + `/projects/roundrobin/api/getconfig/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json())
  .then(data => {
    courtCount = parseInt(data.courtCount)
    minutes = parseInt(data.minutes)
    document.getElementById('nCourts').value = courtCount
    document.getElementById('minutes').value = minutes
  })
  .catch(error => {
    console.error('Search failed:', error);
  })
}

function restoreSelectState() {
  const cookies = document.cookie.split(';'); // Get all cookies and split them
  let minuteState = null;

  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.startsWith('minuteState=')) {
      minuteState = cookie.substring('minuteState='.length);
      break;
    }
  }

  if (minuteState) {
    document.getElementById('minutes').value = minuteState; // Set the selected value
  }

  restoreConfig()

  restoreActivePlayers()

  loadTimer()
  
}

function generateGame() {
  
  document.getElementById('loading').textContent = "Loading..."
  document.querySelector('.games').innerHTML = ""

  fetch(origin + `/projects/roundrobin/api/getnextgame/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json() )
  .then(data => {
    console.log(data)
    document.getElementById('loading').textContent = ""
    nextGames = document.querySelector('.games')
    for (let game of data.games) {
      let court = document.createElement('div')
      court.classList.add("court")
      let topLeft = document.createElement('div')
      topLeft.classList.add("top-left")
      topLeft.innerText = "Court"
      court.appendChild(topLeft)
      let courtNumber = document.createElement('div')
      courtNumber.classList.add("court-number")
      courtNumber.innerText = game.courtNumber
      court.appendChild(courtNumber)
      let bottomLeft = document.createElement('div')
      bottomLeft.classList.add("bottom-left")
      bottomLeft.innerText = "Court"
      court.appendChild(bottomLeft)
      let teamOne = document.createElement('div')
      teamOne.classList.add("team-one", "team")
      let player = document.createElement('div')
      player.classList.add("player")
      player.innerText = game.teamOne[0]
      teamOne.appendChild(player)
      player = document.createElement('div')
      player.classList.add("player")
      player.innerText = game.teamOne[1]
      teamOne.appendChild(player)
      court.appendChild(teamOne)
      let teamTwo = document.createElement('div')
      teamTwo.classList.add("team-two", "team")
      player = document.createElement('div')
      player.classList.add("player")
      player.innerText = game.teamTwo[0]
      teamTwo.appendChild(player)
      player = document.createElement('div')
      player.classList.add("player")
      player.innerText = game.teamTwo[1]
      teamTwo.appendChild(player)
      court.appendChild(teamTwo)
      let scores = document.createElement('div')
      scores.classList.add('scores')
      let teamOneScore = document.createElement('input')
      teamOneScore.classList.add('team-one-score', 'score')
      teamOneScore.type = "text"
      teamOneScore.placeholder = "0"
      scores.appendChild(teamOneScore)
      let teamTwoScore = document.createElement('input')
      teamTwoScore.classList.add('team-two-score', 'score')
      teamTwoScore.type = "text"
      teamTwoScore.placeholder = "0"
      scores.appendChild(teamTwoScore)
      court.appendChild(scores)
      nextGames.appendChild(court)
    }
  })
  .catch(error => {
    console.error('Search failed:', error);
    document.getElementById('loading').textContent = JSON.stringify(data)
  })
}

function resetHistory() {

  fetch(origin + `/projects/roundrobin/api/resetHistory/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json() )
  .then(data => {
    console.log(data)
    document.getElementById('loading').textContent = JSON.stringify(data)
  })
  .catch(error => {
    console.error('Error:', error);
    document.getElementById('loading').textContent = 'There was an error clearing the game history.'
    return
  })

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

function loadTimer() {
fetch(origin + `/projects/roundrobin/api/gettimer/`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json())
  .then(data => {
  function updateCountdown() {
    const now = new Date().getTime();
    const distance = endTime - now;

    if (distance <= 0) {
      clearInterval(timer);
      document.getElementById("countdown").innerHTML = "⏰ Time's up!";
      return;
    }

    const minutes = Math.floor((distance / 1000) / 60);
    const seconds = Math.ceil((distance / 1000) % 60);
    const displayMinutes = seconds === 60 ? minutes + 1 : minutes;
    const displaySeconds = seconds === 60 ? 0 : seconds;

    // Format with leading zero
    const display = `${displayMinutes}:${displaySeconds < 10 ? "0" : ""}${displaySeconds}`;
    document.getElementById("countdown").textContent = display;
  }

  let endTime = data.endTime
  const timer = setInterval(updateCountdown, 1000);
  updateCountdown();

  })
  .catch(error => {
    console.error('Search failed:', error);
  })
}

// Call the function when the page loads
window.onload = restoreSelectState;

