import { makeAutoObservable } from "mobx";
import { IAnalysis } from "../models/IAnalysis";

export default class HistoryStore {
    history = {} as IAnalysis[] | undefined;

    constructor() {
        makeAutoObservable(this);
        this.history = undefined;
    }

    setHistory(history: IAnalysis[]) {
        this.history = history;
    }
}