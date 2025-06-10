// Custom getrandom implementation for Solana BPF
// This provides a minimal implementation to satisfy getrandom requirements

use getrandom::{register_custom_getrandom, Error};

pub fn solana_getrandom(buf: &mut [u8]) -> Result<(), Error> {
    // For Solana BPF, we use a simple deterministic approach
    // In production, this should use Solana's syscalls for randomness
    for (i, byte) in buf.iter_mut().enumerate() {
        *byte = (i as u8).wrapping_mul(17).wrapping_add(42);
    }
    Ok(())
}

register_custom_getrandom!(solana_getrandom);
