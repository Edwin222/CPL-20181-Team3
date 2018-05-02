var firebase = require('firebase');

firebase.initializeApp({
    apiKey: "AIzaSyB5HxyNnazVfufp_EkdOytdil8lm9EiYFs",
    authDomain: "fir-5f8d5.firebaseapp.com",
    databaseURL: "https://fir-5f8d5.firebaseio.com",
    storageBucket: "fir-5f8d5.appspot.com",
    messagingSenderId: "726401611689"
});

var starCountRef = firebase.database().ref('name/first');
starCountRef.on('value', function (snapshot) {
    console.log(snapshot.val());
});

firebase.database().ref('name').set({
    first: "song",
    last: "yj"
});

console.log("change name : song / yj");