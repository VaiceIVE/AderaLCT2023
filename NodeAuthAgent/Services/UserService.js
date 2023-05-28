const db = require('../db')
const UserModel = require('../Models/UserModel')
const bcrypt = require('bcrypt')
const TokenService = require('./TokenService')
const UserDTO = require("../DTOs/UserDTO")
const ApiError = require('../Errors/ApiError')

class UserService
{
    async Register(username, email, password)
    {
        db()

        const candidate = await UserModel.findOne({email: email})

        if (candidate)
        {
            throw ApiError.BadRequest("Email занят!")
        }

        const hashpass = await bcrypt.hash(password, 5)

        const NewUser = await UserModel.create(
            {
                role: 'user',
                username: username,
                email: email,
                password: hashpass
            }
        )

        const userDto = new UserDTO(NewUser)

        const tokens = TokenService.GenerateTokens({...userDto})

        await TokenService.SaveToken(userDto.id, tokens.refreshToken)

        return {...tokens, user: userDto}
    }

    async Login(email, password, role)
    {
        db()

        const user = await UserModel.findOne({email: email})

        if (!user)
        {
            throw ApiError.BadRequest("Нет польщователя с таким email!")
        }

        const isPassEquals = await bcrypt.compare(password, user.password)

        if(!isPassEquals)
        {
            throw ApiError.BadRequest("Неверный пароль!")
        }

        user.role = role;

        await user.save();

        const userDto = new UserDTO(user)

        const tokens = TokenService.GenerateTokens({...userDto})

        await TokenService.SaveToken(userDto.id, tokens.refreshToken)

        return {...tokens, user: userDto}
    }

    async Refresh(refreshToken)
    {
        db()

        if (!refreshToken)
        {
            throw ApiError.UnauthorizedError();
        }

        const userData = await TokenService.ValidateRefreshToken(refreshToken);
        const dbToken = await TokenService.FindToken(refreshToken);

        if (!userData || !dbToken)
        {
            throw ApiError.UnauthorizedError();
        }

        const user = await UserModel.findById(userData.id);
        const userDto = new UserDTO(user)
        const tokens = TokenService.GenerateTokens({...userDto})

        await TokenService.SaveToken(user.id, tokens.refreshToken)

        return {...tokens, user: userDto}

    }

    async Logout(refreshToken)
    {
        const token = TokenService.RemoveToken(refreshToken)

        return token
    }
}

module.exports = new UserService()