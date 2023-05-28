const axios = require("axios");

class UserService
{
    async Login(email, password, role)
    {
        var res = null
        await axios.post(process.env.AUTH_AGENT_URL + "/login", {email, password, role}).then(function(response) {
            res =  response.data
        })
        .catch(function(error) {
            res =  error.response.data
        });  
        return res;
    }

    async Register(username, email, password, role)
    {
        var res = null
        await axios.post(process.env.AUTH_AGENT_URL + "/register", {username, email, password, role}).then((response) => {
            res = response.data
        })
        .catch((error) => {
            console.log(error.response.data)
            res = error.response.data
        });
        return res;
    }

    async Refresh(refreshToken)
    {
        var res = null
        await axios.post(process.env.AUTH_AGENT_URL + "/refresh", {refreshToken}).then(function(response) {
            res =  response.data
        })
        .catch(function(error) {
            res =  error.response.data
        }); 
        return res;
    }

    async Logout(refreshToken)
    {
        var res = null
        await axios.post(process.env.AUTH_AGENT_URL + "/logout", {refreshToken}).then(function(response) {
            res =  response.data
        })
        .catch(function(error) {
            res =  error.response.data
        });  
        return res;
    }
}

module.exports = new UserService()