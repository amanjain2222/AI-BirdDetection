

function getUser() {
        if (sessionStorage.getItem("idToken")) {
          const payload = JSON.parse(atob(sessionStorage.getItem("idToken").split('.')[1]));
          return payload.sub;
        }
    return "Error: No user found";
}

export default getUser;
