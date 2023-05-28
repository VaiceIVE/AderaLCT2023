const UserService = require('../Services/UserService');

class UserController
{
    async Register(req, res, next)
    { 
         // #swagger.description = 'Метод для регистрации пользователей. Роль пользователя указывается для упрощения процесса тестирования. Таким образом один пользователь может пробовать разные роли.'
        /*  #swagger.parameters['body'] = {
                in: 'body',
                description: 'Информация о пользователе для регистрации',
                schema: { $ref: '#/definitions/UserReg'}
        } 
            #swagger.responses[200] = {
            description: 'Информация о залогиненном пользователе',
            schema: { $ref: '#/definitions/UserResponse' }
        } 
        */
        
        try
        {
            const {username, email, password} = req.body;

            const userData = await UserService.Register(username, email, password);
    
            res.json(userData)
        }
        catch(e)
        {
            console.log(e)
            next(e)
        }
        

    }

    async Login(req, res, next)
    {
         // #swagger.description = 'Метод для логина пользователей. Роль пользователя указывается для упрощения процесса тестирования. Таким образом один пользователь может пробовать разные роли.'
        /*  #swagger.parameters['body'] = {
                in: 'body',
                description: 'Информация о пользователе для логина',
                schema: { $ref: '#/definitions/UserLog'}
        }
            #swagger.responses[200] = {
                description: 'Информация о залогиненном пользователе',
                schema: { $ref: '#/definitions/UserResponse' }
        }  */
        try {
            const {email, password, role} = req.body;

            const userData = await UserService.Login(email, password, role)

            res.json(userData)
            
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async Refresh(req, res, next)
    {
        // #swagger.description = 'Метод для обновления информации пользователей. Использует технологию JWT'
        /*  #swagger.parameters['body'] = {
                in: 'body',
                description: 'Токен обновления пользователя',
                schema: { $ref: '#/definitions/RefreshToken'}
        }
            #swagger.responses[200] = {
                description: 'Информация о залогиненном пользователе',
                schema: { $ref: '#/definitions/UserResponse' }
        }  */
        try {

            const {refreshToken} = req.body

            const userData = await UserService.Refresh(refreshToken)

            res.json(userData)
            
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async Logout(req, res, next)
    {  
         // #swagger.description = 'Метод для выхода из аккаунта.'
        /*  #swagger.parameters['body'] = {
                in: 'body',
                description: 'Токен обновления пользователя',
                schema: { $ref: '#/definitions/RefreshToken'}
        }
            #swagger.responses[200] = {
                description: 'Информация о удалении пользователя',
                schema: { $ref: '#/definitions/LogOut' }
        }  */
        try {

            const {refreshToken} = req.body

            const userData = await UserService.Logout(refreshToken)

            res.json(userData)
            
        } catch (e) {
            console.log(e)
            next(e)
        }
    }
}

module.exports = new UserController()
