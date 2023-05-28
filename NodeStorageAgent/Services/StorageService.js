const path = require('path')
const fileSystem = require('fs')
const DownloadFile = require('../Functions/DownloadFile')
class StorageService
{
    GetFile(filename)
    {
        var filePath = path.join(__dirname, "../Storage", filename);

        var readStream = fileSystem.createReadStream(filePath);

        return readStream;
    }

    async DownloadFiles(url, types)
    {
        var filenames = []
        for (const type of types)
        {
            const name = type + new Date().toISOString() + ".xlsx";
            const file =  await DownloadFile(url + '/' + type, "Storage/" + name)
                
            if(file)
            {
                filenames.push(name);
            }
            else{
                throw new Error();
            }
        }
        return filenames
    }
    List()
    {
        let res = []
        fileSystem.readdirSync('./Storage/')
        .forEach((file) => 
        {
            res.push(file)
        })
        return res;
    }
}


module.exports = new StorageService()