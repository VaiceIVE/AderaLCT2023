import { makeAutoObservable } from "mobx";

export default class DatabaseStore {
    database =  [] as string[] | undefined;

    constructor() {
        makeAutoObservable(this);
        this.database = undefined;
    };

    setDatabase(database: string[]) {
        this.database = database;
    };
};