import type { Client } from '..';
import Wallet from '.';
declare enum FaucetNetwork {
    Testnet = "faucet.altnet.rippletest.net",
    Devnet = "faucet.devnet.rippletest.net"
}
declare function fundWallet(this: Client, wallet?: Wallet | null, options?: {
    faucetHost?: string;
}): Promise<{
    wallet: Wallet;
    balance: number;
}>;
declare function getFaucetHost(client: Client): FaucetNetwork | undefined;
export default fundWallet;
declare const _private: {
    FaucetNetwork: typeof FaucetNetwork;
    getFaucetHost: typeof getFaucetHost;
};
export { _private };
//# sourceMappingURL=fundWallet.d.ts.map