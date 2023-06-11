import { makeAutoObservable } from "mobx";

export default class MapsStore {
    addresses: string[] = [];
    causes: string[][] = [];
    workname: string[][] = [];

    constructor() {
        makeAutoObservable(this);
    };

    setAddresses(address: string) {
        this.addresses.push(address);
    };

    setCauses(causes: string[]) {
        this.causes.push(causes);
    }

    setWorkname(workname: string[]) {
        this.workname.push(workname)
    }

    mapsClear() {
        this.addresses = [];
        this.causes = [];
        this.workname = [];
    }
}