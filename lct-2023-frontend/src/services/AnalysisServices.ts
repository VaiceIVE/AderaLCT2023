import { AxiosResponse } from "axios";
import $api from "../http";
import { IAnalysis } from "../models/IAnalysis";

export default class AnalysisServices {

    static async baseAnalysis(): Promise<AxiosResponse<IAnalysis>>{
        return $api.get<IAnalysis>('/analysis/base');
    };

    static async smartAnalysisDatabase(obj: string, 
        date: [Date | null, Date | null], work: string): Promise<AxiosResponse<IAnalysis>> {
            return $api.post<IAnalysis>('/analysis/advanced', {obj, date, work})
    };

    static async smartAnalysisUrl(object: string, 
        date: [Date | null, Date | null], work: string, url: string): Promise<AxiosResponse<IAnalysis>> {
            return $api.post<IAnalysis>('/analysis/advanced/url', {object, date, work, url})
    };

    static async selectAnalysis(id: string): Promise<AxiosResponse<IAnalysis>> {
        return $api.get<IAnalysis>('/analysis' + '/' + id);
    };

    static async saveAnalysis(analysis: IAnalysis): Promise<AxiosResponse<string>> {
        return $api.post<string>('/analysis/update', analysis);
    };

    static async fileExport(name: string, type:string, id: string): Promise<AxiosResponse<Blob>> {
        return $api.get<Blob>(`/analysis/${type.substring(1)}byid/${id}/${name}`, {responseType: 'blob'});
    };

    static async setWorktypes() : Promise<AxiosResponse<string[]>> {
        return $api.get<string[]>(`/analysis/worktypes`);
    };

    static async setObjcategories() : Promise<AxiosResponse<string[]>> {
        return $api.get<string[]>(`/analysis/objcategories`);
    };
};