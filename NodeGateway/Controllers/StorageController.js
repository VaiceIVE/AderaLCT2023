const axios = require('axios')
const StorageService = require('../Services/StorageService')
const fs = require('fs')
class StorageController
{
    async GetFile(req, res, next)
    {
        try {
            const {filename} = req.params

            const stream = await StorageService.GetFile(filename);

            stream.pipe(res).on('finish', () => {fs.unlink(`Temp/${filename}`, (err) => {err ? console.log(err) : null})});
        } catch (error) {
            console.log(err)
            next(err)
        }
        
    }

    async GetList(req, res, next)
    {
        try {
            const response = await StorageService.GetAll()
        
            res.json(response)
        } catch (error) {
            console.log(err)
            next(err)
        }
       
    }
}

module.exports = new StorageController()