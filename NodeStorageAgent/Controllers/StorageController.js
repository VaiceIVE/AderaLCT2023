const StorageService = require('../Services/StorageService')
class StorageController
{
    async UploadFile(req, res, next)    
    {   
         /* #swagger.description = 'Метод для загрузки одного файла в файловую систему'
            
          #swagger.consumes = ['multipart/form-data']  
          #swagger.parameters['file'] = {
              in: 'formData',
              type: 'file',
              required: 'true',
              description: 'Входящий файл',
        } 
            #swagger.responses[200] = {
            description: 'Информация о названии файла в файловой системе хранилища',
            schema: 'FileAdressPlusDate.xlsx'
        } 
        */
        try {
            res.json(req.file.originalname)
        } catch (error) {
            res.json(error)
        }
    }

    async GetFile(req, res, next)
    {
        /* #swagger.description = 'Метод для получения файла по названию из файловой системы хранилища'
            
            #swagger.parameters['filename'] ={
                schema: 'FileAdressPlusDate.xlsx'
            }

            #swagger.responses[200] = {
            description: 'Файл, если есть',
            schema: 'FileAdressPlusDate.xlsx'
        } 
        */
        try {
            const {filename} = req.params

            const readStream = StorageService.GetFile(filename)
            
            res.setHeader('Content-disposition', 'attachment; filename=' + filename);
            res.writeHead(200, {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            });

            return readStream.pipe(res)
        } catch (error) {
            res.json(error)
        }
    }

    async DownloadByUrl(req, res, next)
    {
         /* #swagger.description = 'Метод, выполняющий загрузку файлов таблиц с данными со стороннего сервиса, адрес которого указан в запросе. Типы файлов, которые необходимо искать на сервисе передаются массивом вутри запроса.'
            
            #swagger.parameters['body'] = {
                in: 'body',
                description: 'Адрес сервиса, с которого будут получаться данные и типы получаемых таблиц',
                schema: { $ref: '#/definitions/UrlData'}
            }

            #swagger.responses[200] = {
            description: 'Имена файлов в файловой системе хранилища',
            schema: ['FirstFileAdressPlusDate.xlsx', 'SecondFileAdressPlusDate.xlsx']
        } 
        */

        const {url} = req.body

        const {types} = req.body

        const filenames = StorageService.DownloadFiles(url, types)

        res.json(filenames)
    }

    async List(req, res, next)
    {
        /* #swagger.description = 'Метод для получения имен таблиц в файловой системе хранилища.'

            #swagger.responses[200] = {
            description: 'Имена файлов в файловой системе хранилища',
            schema: ['FirstFileAdressPlusDate.xlsx', 'SecondFileAdressPlusDate.xlsx']
        } 
        */

        res.json(StorageService.List())
    }
}

module.exports = new StorageController()