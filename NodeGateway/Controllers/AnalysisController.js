const AnalysisService = require("../Services/AnalysisService")
const StorageService = require("../Services/StorageService")
const StorageController = require("./StorageController")
const fs = require('fs')

class AnalysisController
{
    async BaseAnalysis(req, res, next)
    {
        try {
            const response = await AnalysisService.BaseAnalysis()

            res.json(response)
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async AdvancedAnalysis(req, res, next)
    {
        try {
            const {obj, work, date} = req.body

            const response = await AnalysisService.AdvancedAnalysis(obj, work, date)

            console.log(response)

            res.json(response)
        } catch (e) {
            console.log(e)
            next(e)
        }

    }

    async AdvancedAnalysisFile(req, res, next)
    {

        try {



            const files = req.files

            var filenames = []

            console.log(files[0])

            files[0].type = "Type"

            console.log(files[0])


            for (const file of files)
            {
                filenames.push(file.originalname)
            }

            const resfilenames = await StorageService.Upload(filenames)

            for (const file of files)
            {
                fs.unlink('./Storage/' + file.originalname, (err) => {if(err){console.log(err)}});
            }

            res.json(resfilenames)
        } catch (e) {
            console.log(e)
        }
        
    }

    async AdvancedAnalysisUrl(req, res, next)
    {
        // Предполагается, что одна ссылка ведет на сервис с кучей таблиц, где есть вся информация
        const {url} = req.body
        await StorageService.UploadByUrl(url)
    }

    async Worktypes(req, res, next)
    {
        try {
            const response = await AnalysisService.WorkTypes()

            res.json(response)
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async ObjTypes(req, res, next)
    {
        try {
            const response = await AnalysisService.ObjTypes()

            res.json(response)
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async XlsxById(req, res, next)
    {
        const {id, name} = req.params
        try {
            const stream = await AnalysisService.XlsxById(id, name)
            res.set({'Content-Disposition': `attachment; filename="${name}.xlsx"`, 'Content-Type': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
            stream.pipe(res).on('finish', () => {fs.unlink('Temp/tmp.xlsx', (err) => {err ? console.log(err) : null})});
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async XlsById(req, res, next)
    {
        const {id, name} = req.params
        try {
            const stream = await AnalysisService.XlsById(id, name)
            res.set({'Content-Disposition': `attachment; filename="${name}.xls"`, 'Content-Type': "application/vnd.ms-excel"})
            stream.pipe(res).on('finish', () => {fs.unlink('Temp/tmp.xls', (err) => {err ? console.log(err) : null})});
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async CsvById(req, res, next)
    {
        const {id, name} = req.params
        try {
            const stream = await AnalysisService.CsvById(id, name)
            res.set({'Content-Disposition': `attachment; filename="${name}.csv"`, 'Content-Type': "application/vnd.ms-excel"})
            stream.pipe(res).on('finish', () => {fs.unlink('Temp/tmp.csv', (err) => {err ? console.log(err) : null})});
        } catch (e) {
            console.log(e)
            next(e)
        }
    }

    async GetHistory(req, res, next)
    {
        try {
            const response = await AnalysisService.GetHistory()

            res.json(response)
        } catch (e) {
            console.log(e)
            next(e)
        }    
    }

    async AnalysisDataById(req, res, next)
    {
        try {
            const {id} = req.params

            const response = await AnalysisService.AnalysisDataById(id)

            res.json(response)
        } catch (e) {
            console.log(e)
            next(e)
        }    
    }

    async UpdateAnalysis(req, res, next)
    {
        try {
            const newdata = req.body

            const response = await AnalysisService.UpdateAnalysis(newdata)

            res.json(response)
        } catch (e) {
            console.log(e)
            next(e)
        }    
    }
}

module.exports = new AnalysisController()
