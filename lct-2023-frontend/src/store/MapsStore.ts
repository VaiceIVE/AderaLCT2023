import { makeAutoObservable } from "mobx";

export default class MapsStore {
    addresses: string[] = [];
    priority: string[] = [];
    workname: string[][] = [];

    constructor() {
        makeAutoObservable(this);
    };

    setAddresses(address: string) {
        this.addresses.push(address);
    };

    setPriority(priority: string) {
        this.priority.push(priority);
    }

    setWorkname(workname: string[]) {
        this.workname.push(workname)
    }

    mapsClear() {
        this.addresses = [];
        this.priority = [];
        this.workname = [];
    }
}