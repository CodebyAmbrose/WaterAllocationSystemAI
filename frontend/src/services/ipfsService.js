/**
 * IPFS Service
 * Provides functions to interact with IPFS for retrieving prediction metadata
 */

import { create } from 'ipfs-http-client';

// Connect to a public IPFS gateway
// Note: For production, consider using your own IPFS node or a dedicated IPFS service
const ipfs = create({
  host: 'ipfs.infura.io',
  port: 5001,
  protocol: 'https',
  apiPath: '/api/v0'
});

/**
 * Fetch data from IPFS using a CID (Content Identifier)
 * @param {string} cid - The IPFS content identifier
 * @returns {Promise<Object>} - Promise that resolves to the parsed JSON data
 */
export async function fetchFromIPFS(cid) {
  if (!cid) {
    throw new Error('CID is required to fetch data from IPFS');
  }
  
  try {
    console.log(`Fetching data from IPFS with CID: ${cid}`);
    const stream = ipfs.cat(cid);
    
    let data = '';
    for await (const chunk of stream) {
      data += new TextDecoder().decode(chunk);
    }
    
    return JSON.parse(data);
  } catch (error) {
    console.error('Error fetching from IPFS:', error);
    throw error;
  }
}

/**
 * Check if an IPFS CID exists and is accessible
 * @param {string} cid - The IPFS content identifier to check
 * @returns {Promise<boolean>} - Promise that resolves to true if the CID exists
 */
export async function checkCidExists(cid) {
  if (!cid) return false;
  
  try {
    // We'll just try to get the stat for the CID
    await ipfs.block.stat(cid);
    return true;
  } catch (error) {
    console.error('Error checking CID:', error);
    return false;
  }
}

/**
 * Format an IPFS Gateway URL for a given CID
 * @param {string} cid - The IPFS content identifier
 * @returns {string} - The gateway URL
 */
export function getIPFSGatewayUrl(cid) {
  if (!cid) return '';
  return `https://ipfs.io/ipfs/${cid}`;
} 