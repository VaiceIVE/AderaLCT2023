import { IAnalysisResult } from "./IAnalysisResult";

export interface IAnalysis {
    result: IAnalysisResult[] | undefined,
    type: string | undefined;
    id: string;
    date: string;
    criterias: string[] | undefined;
};