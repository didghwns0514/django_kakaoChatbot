"use strict";

// Function to check Whether both passwords
// is same or not.
function checkPassword() {

    let password1 = document.getElementById( 'password1' ).value;
    let password2 = document.getElementById( 'password2' ).value;

    // If password not entered
    if (password1 === '') {
        console.log("Password - Missing");
        alert("Please enter Password");
    }
    // If confirm password not entered
    else if (password2 === ''){
        console.log("Password - Not equal");
        alert ("Please enter confirm password");
    }
    // If Not same return False.
    else if (password1 !== password2) {
        alert ("\nPassword did not match: Please try again");
        console.log("Password - Not equal");
        return false;
    }

    // If same return True.
    else{
        alert("Password Match: Please Continue");
        console.log("Password - Correct");
        return true;
    }
}