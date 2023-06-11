import { makeAutoObservable } from "mobx";
import { IAnalysis } from "../models/IAnalysis";
import AnalysisServices from "../services/AnalysisServices";

export default class AnalysisStore {
    isBaseLoading = false;
    isSmartLoading = false;
    currentBaseAnalysis = {} as IAnalysis | undefined;
    currentSmartAnalysis = {} as IAnalysis | undefined;
    analysis = {} as IAnalysis | undefined;

    constructor() {
        makeAutoObservable(this);
        this.currentBaseAnalysis = undefined;
        this.currentSmartAnalysis = undefined;
    }

    setBaseLoading(isLoading: boolean) {
        this.isBaseLoading = isLoading;
    };

    setSmartLoading(isLoading: boolean) {
        this.isSmartLoading = isLoading;
    };

    setAnalysis(analysis: IAnalysis | undefined) {
        this.analysis = analysis;
    }

    setCurrentBaseAnalysis(analysis: IAnalysis | undefined) {
        this.currentBaseAnalysis = analysis;
    };

    setCurrentSmartAnalysis(analysis: IAnalysis | undefined) {
        this.currentSmartAnalysis = analysis;
    };

    async baseAnalysis() {
        this.setBaseLoading(true);
        try {
            const response = await AnalysisServices.baseAnalysis();
            console.log(response.data)
            this.setCurrentBaseAnalysis(response.data);
        } catch (e: any) {
            console.log(e.response?.data?.message);
        } finally {
            this.setBaseLoading(false);
        }
    };

    async smartAnalysisDatabase(object: string, 
        date: [Date | null, Date | null], work: string) {
        this.setSmartLoading(true);
        try {
            const response = await AnalysisServices.smartAnalysisDatabase(object, date, work);
            console.table(response.data);
            this.setCurrentSmartAnalysis(response.data);
        } catch (e: any) {
            console.log(e.response?.data?.message);
        } finally {
            this.setSmartLoading(false);
        }
    };


    async smartAnalysisURL(object: string, 
        date: [Date | null, Date | null], work: string, url: string) {
        this.setSmartLoading(true);
        try {
            const response = await AnalysisServices.smartAnalysisUrl(object, date, work, url);
            console.table(response.data);
            this.setCurrentSmartAnalysis(response.data);
        } catch (e: any) {
            console.log(e.response?.data?.message);
        } finally {
            this.setSmartLoading(false);
        }
    };

};