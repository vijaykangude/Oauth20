const express = require("express");
const passport = require("passport");
const googleStrategy = require("passport-google-oauth20");
const app = express();
const port = 3000;



passport.use(new googleStrategy({
  clientID:"385592309513-eh14g03rl6j88ni8bbbkano7drtj4mgm.apps.googleusercontent.com",
  clientSecret:"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",
  callbackURL:"/auth/google/callback"
}, (accessToken,refreshToken,profile,done) =>{
  console.log(accessToken);
  console.log(refreshToken);
  console.log(profile);
}));

app.get('/', (req, res) =>{
  res.sendFile(__dirname + "/" + "./public/index.html");
})

app.get('/login',passport.authenticate("google",{
  scope: ["profile"]
}));

app.get("/auth/google/callback", passport.authenticate("google",{ failureRedirect: '/login' }), (req, res) =>{
    // Successful authentication, redirect home.
    res.redirect('/');  
});

app.listen(port , () =>{
  console.log(`Application Started At Port: ${port}!`);
});