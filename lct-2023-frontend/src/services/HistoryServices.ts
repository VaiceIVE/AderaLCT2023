import { AxiosResponse } from "axios";
import $api from "../http";
import { IAnalysis } from "../models/IAnalysis";

export default class HistoryServices {
    static fetchHistory(): Promise<AxiosResponse<IAnalysis[]>> {
        return $api.get<IAnalysis[]>('/analysis/history');
    };
};
