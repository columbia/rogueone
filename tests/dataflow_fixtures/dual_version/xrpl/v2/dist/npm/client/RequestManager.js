"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const errors_1 = require("../errors");
class RequestManager {
    constructor() {
        this.nextId = 0;
        this.promisesAwaitingResponse = new Map();
    }
    resolve(id, response) {
        const promise = this.promisesAwaitingResponse.get(id);
        if (promise == null) {
            throw new errors_1.XrplError(`No existing promise with id ${id}`);
        }
        clearTimeout(promise.timer);
        promise.resolve(response);
        this.deletePromise(id);
    }
    reject(id, error) {
        const promise = this.promisesAwaitingResponse.get(id);
        if (promise == null) {
            throw new errors_1.XrplError(`No existing promise with id ${id}`);
        }
        clearTimeout(promise.timer);
        promise.reject(error);
        this.deletePromise(id);
    }
    rejectAll(error) {
        this.promisesAwaitingResponse.forEach((_promise, id, _map) => {
            this.reject(id, error);
            this.deletePromise(id);
        });
    }
    createRequest(request, timeout) {
        let newId;
        if (request.id == null) {
            newId = this.nextId;
            this.nextId += 1;
        }
        else {
            newId = request.id;
        }
        const newRequest = JSON.stringify(Object.assign(Object.assign({}, request), { id: newId }));
        const timer = setTimeout(() => this.reject(newId, new errors_1.TimeoutError()), timeout);
        if (timer.unref) {
            timer.unref();
        }
        if (this.promisesAwaitingResponse.has(newId)) {
            throw new errors_1.XrplError(`Response with id '${newId}' is already pending`);
        }
        const newPromise = new Promise((resolve, reject) => {
            this.promisesAwaitingResponse.set(newId, { resolve, reject, timer });
        });
        return [newId, newRequest, newPromise];
    }
    handleResponse(response) {
        var _a, _b;
        if (response.id == null ||
            !(typeof response.id === 'string' || typeof response.id === 'number')) {
            throw new errors_1.ResponseFormatError('valid id not found in response', response);
        }
        if (!this.promisesAwaitingResponse.has(response.id)) {
            return;
        }
        if (response.status == null) {
            const error = new errors_1.ResponseFormatError('Response has no status');
            this.reject(response.id, error);
        }
        if (response.status === 'error') {
            const errorResponse = response;
            const error = new errors_1.RippledError((_a = errorResponse.error_message) !== null && _a !== void 0 ? _a : errorResponse.error, errorResponse);
            this.reject(response.id, error);
            return;
        }
        if (response.status !== 'success') {
            const error = new errors_1.ResponseFormatError(`unrecognized response.status: ${(_b = response.status) !== null && _b !== void 0 ? _b : ''}`, response);
            this.reject(response.id, error);
            return;
        }
        delete response.status;
        this.resolve(response.id, response);
    }
    deletePromise(id) {
        this.promisesAwaitingResponse.delete(id);
    }
}
exports.default = RequestManager;
//# sourceMappingURL=RequestManager.js.map