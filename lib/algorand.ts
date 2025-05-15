import algosdk from 'algosdk';

let algodClient: algosdk.Algodv2 | null = null;

export function getAlgodClient(): algosdk.Algodv2 {
  if (!algodClient) {
    const token = process.env.NEXT_PUBLIC_ALGORAND_NODE_TOKEN || '';
    const server = process.env.NEXT_PUBLIC_ALGORAND_NODE_SERVER || 'https://testnet-api.algonode.cloud';
    const port = process.env.NEXT_PUBLIC_ALGORAND_NODE_PORT || '';
    algodClient = new algosdk.Algodv2(token, server, port);
  }
  return algodClient;
} 