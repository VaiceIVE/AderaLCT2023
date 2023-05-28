const axios = require('axios')
const uploader = require('../Services/UploadHelperService')
const DownloadFile = require('../Functions/DownloadFile')
const fs = require('fs')

class AnalysisService
{
    async BaseAnalysis()
    {
        let res = null
        await axios.get(process.env.ANALYSIS_AGENT_URL + "/base")
        .then((response) => {res = response.data})
        .catch((err) => {console.log(err);res = err.response.data})
        return res
    }

    async AdvancedAnalysis(obj, work, date)
    {
        let res = null
        await axios.post(process.env.ANALYSIS_AGENT_URL + "/advanced", {'obj': obj, 'work': work, 'date': date})
        .then((response) => {
            console.log(response.data)
            res = response.data 
        })
        .catch((err) => {console.log(err);res = err.response.data})
        return res
    }   

    async WorkTypes()
    {
        let res = null
        await axios.get(process.env.ANALYSIS_AGENT_URL + "/worktypes")
        .then((response) => {res = response.data})
        .catch((err) => {console.log(err);res = err.response.data})
        return res
    }

    async ObjTypes()
    {
        let res = null
        await axios.get(process.env.ANALYSIS_AGENT_URL + "/objcategories")
        .then((response) => {res = response.data})
        .catch((err) => {console.log(err);res = err.response.data})
        return res
    }

    async XlsxById(id, name)
    {
        await DownloadFile(process.env.ANALYSIS_AGENT_URL + `/xlsxbyid/${id}/${name}`, 'Temp/tmp.xlsx')
        var readStream = fs.createReadStream('Temp/tmp.xlsx');
        return readStream
    }

    async XlsById(id, name)
    {
        await DownloadFile(process.env.ANALYSIS_AGENT_URL + `/xlsbyid/${id}/${name}`, 'Temp/tmp.xls')
        var readStream = fs.createReadStream('Temp/tmp.xls');
        return readStream
    }

    async CsvById(id, name)
    {
        await DownloadFile(process.env.ANALYSIS_AGENT_URL + `/csvbyid/${id}/${name}`, 'Temp/tmp.csv')
        var readStream = fs.createReadStream('Temp/tmp.csv');
        return readStream
    }

    async GetHistory()
    {

        let res = null
        await axios.get(process.env.ANALYSIS_AGENT_URL + "/history")
        .then((response) => {res = response.data})
        .catch((err) => {res = err.response.data})
        return res
    }

    async AnalysisDataById(id)
    {
        let res = null
        await axios.get(process.env.ANALYSIS_AGENT_URL + `/analyze/${id}`)
        .then((response) => {res = response.data})
        .catch((err) => {res = err.response.data})
        return res
    }

    async UpdateAnalysis(newdata)
    {
        let res = null
        await axios.post(process.env.ANALYSIS_AGENT_URL + `/analyze/update`, newdata)
        .then((response) => {res = response.data})
        .catch((err) => {res = err.response.data})
        return res
    }
    
}

module.exports = new AnalysisService()
