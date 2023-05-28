const express = require('express')
const AnalysisController = require('../Controllers/AnalysisController')
const uploader = require('../Services/UploadHelperService')

const router = express()



router.get('/base', AnalysisController.BaseAnalysis)
router.get('/worktypes', AnalysisController.Worktypes)
router.get('/objcategories', AnalysisController.ObjTypes)
router.get('/xlsxbyid/:id/:name', AnalysisController.XlsxById)
router.get('/xlsbyid/:id/:name', AnalysisController.XlsById)
router.get('/csvbyid/:id/:name', AnalysisController.CsvById)
router.get('/history', AnalysisController.GetHistory)
router.get('/:id', AnalysisController.AnalysisDataById)
router.post('/update', AnalysisController.UpdateAnalysis)
router.post('/advanced', AnalysisController.AdvancedAnalysis)
router.post('/advanced/url', AnalysisController.AdvancedAnalysisUrl)
router.post('/advanced/file', uploader.array('files'), AnalysisController.AdvancedAnalysisFile)




module.exports = router