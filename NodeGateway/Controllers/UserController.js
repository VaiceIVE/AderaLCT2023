const UserService = require('../Services/UserService');

class UserController
{
    async Register(req, res, next)
    {
        try
        {
            const {username, email, password, role} = req.body;

            const response = await UserService.Register(username, email, password, role)

            res.json(response)
        }
        catch(e)
        {
            console.log(e)
            next(e)
        }
    }

    async Login(req, res, next)
    {
        try {
            const {email, password, role} = req.body;

            const response = await UserService.Login(email, password, role)

            res.json(response)          
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async Refresh(req, res, next)
    {
        try {

            const {refreshToken} = req.body

            const response = await UserService.Refresh(refreshToken)

            res.json(response)          
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async Logout(req, res, next)
    {
        try {

            const {refreshToken} = req.body

            const response = await UserService.Logout(refreshToken)

            res.json(response)           
        } catch (e) {
            console.log(e)
            next(e)
        }
    }
}

module.exports = new UserController()
