import type { Amount, Currency, Path, StreamType, ResponseOnlyTxInfo } from '../common';
import { Offer } from '../ledger';
import { OfferCreate, Transaction } from '../transactions';
import { TransactionMetadata } from '../transactions/metadata';
import type { BaseRequest, BaseResponse } from './baseMethod';
interface Book {
    taker_gets: Currency;
    taker_pays: Currency;
    taker: string;
    snapshot?: boolean;
    both?: boolean;
}
export interface SubscribeRequest extends BaseRequest {
    command: 'subscribe';
    streams?: StreamType[];
    accounts?: string[];
    accounts_proposed?: string[];
    books?: Book[];
    url?: string;
    url_username?: string;
    url_password?: string;
}
declare type BooksSnapshot = Offer[];
export interface SubscribeResponse extends BaseResponse {
    result: Record<string, never> | LedgerStreamResponse | BooksSnapshot;
}
interface BaseStream {
    type: string;
}
export interface LedgerStream extends BaseStream {
    type: 'ledgerClosed';
    fee_base: number;
    fee_ref: number;
    ledger_hash: string;
    ledger_index: number;
    ledger_time: number;
    reserve_base: number;
    reserve_inc: number;
    txn_count: number;
    validated_ledgers?: string;
}
export interface LedgerStreamResponse {
    fee_base: number;
    fee_ref: number;
    ledger_hash: string;
    ledger_index: number;
    ledger_time: number;
    reserve_base: number;
    reserve_inc: number;
    validated_ledgers?: string;
}
export interface ValidationStream extends BaseStream {
    type: 'validationReceived';
    amendments?: string[];
    base_fee?: number;
    flags: number;
    full: boolean;
    ledger_hash: string;
    ledger_index: string;
    load_fee?: number;
    master_key?: string;
    reserve_base?: number;
    reserve_inc?: number;
    signature: string;
    signing_time: number;
    validation_public_key: string;
}
export interface TransactionStream extends BaseStream {
    status: string;
    type: 'transaction';
    engine_result: string;
    engine_result_code: number;
    engine_result_message: string;
    ledger_current_index?: number;
    ledger_hash?: string;
    ledger_index?: number;
    meta?: TransactionMetadata;
    transaction: Transaction & ResponseOnlyTxInfo;
    validated?: boolean;
    warnings?: Array<{
        id: number;
        message: string;
    }>;
}
export interface PeerStatusStream extends BaseStream {
    type: 'peerStatusChange';
    action: 'CLOSING_LEDGER' | 'ACCEPTED_LEDGER' | 'SWITCHED_LEDGER' | 'LOST_SYNC';
    date: number;
    ledger_hash?: string;
    ledger_index?: number;
    ledger_index_max?: number;
    ledger_index_min?: number;
}
interface ModifiedOfferCreateTransaction extends OfferCreate {
    owner_funds: string;
}
export interface OrderBookStream extends BaseStream {
    status: string;
    type: 'transaction';
    engine_result: string;
    engine_result_code: number;
    engine_result_message: string;
    ledger_current_index?: number;
    ledger_hash?: string;
    ledger_index?: number;
    meta: TransactionMetadata;
    transaction: (Transaction | ModifiedOfferCreateTransaction) & {
        date?: number;
        hash?: string;
    };
    validated: boolean;
}
export interface ConsensusStream extends BaseStream {
    type: 'consensusPhase';
    consensus: 'open' | 'establish' | 'accepted';
}
export interface PathFindStream extends BaseStream {
    type: 'path_find';
    source_account: string;
    destination_account: string;
    destination_amount: Amount;
    full_reply: boolean;
    id: number | string;
    send_max?: Amount;
    alternatives: [] | {
        paths_computed: Path[];
        source_amount: Amount;
    };
}
export declare type Stream = LedgerStream | ValidationStream | TransactionStream | PathFindStream | PeerStatusStream | OrderBookStream | ConsensusStream;
export {};
//# sourceMappingURL=subscribe.d.ts.map