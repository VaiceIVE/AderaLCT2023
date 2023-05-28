const jwt = require('jsonwebtoken')
const db = require('../db')
const TokenModel = require('../Models/TokenModel')


class TokenService
{
    GenerateTokens(payload)
    {
        const accessToken = jwt.sign(payload, process.env.JWT_ACCESS_SECRET, {expiresIn: "24h"})

        const refreshToken = jwt.sign(payload, process.env.JWT_REFRESH_SECRET, {expiresIn: "24d"})

        return{accessToken, refreshToken}
    }

    async SaveToken(id, refreshToken)
    {
        db()

        const tokenData = await TokenModel.findOne({user: id})

        if(tokenData)
        {
            tokenData.refreshToken = refreshToken;
            tokenData.save();
        }

        const token = await TokenModel.create({user: id, refreshToken})

        return token;
    }

    ValidateAccessToken(token)
    {
        try {
            const userData = jwt.verify(token, process.env.JWT_ACCESS_SECRET)

            return userData;
            
        } catch (e) {
            return null
        }

    }

    ValidateRefreshToken(token)
    {
        try {
            const userData = jwt.verify(token, process.env.JWT_REFRESH_SECRET)

            return userData;
            
        } catch (e) {
            return null
        }
    }

    async RemoveToken(refreshToken)
    {
        db()

        const token = TokenModel.deleteOne({refreshToken})
        return token
    }

    async FindToken(refreshToken)
    {
        db()

        const token = TokenModel.findOne({refreshToken})
        return token
    }
}

module.exports = new TokenService()