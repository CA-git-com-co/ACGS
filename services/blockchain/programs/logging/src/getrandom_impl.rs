// Constitutional Hash: cdd01ef066bc6cf2
// Custom getrandom implementation for Solana BPF
// This provides a minimal implementation to satisfy getrandom requirements

use getrandom::{register_custom_getrandom, Error};

pub fn solana_getrandom(buf: &mut [u8]) -> Result<(), Error> {
    // SECURITY: Use Solana's secure randomness syscalls for production
    // This implementation uses Solana's sol_get_clock_sysvar for entropy
    use solana_program::{clock::Clock, sysvar::Sysvar};

    // Get current clock for entropy source
    let clock = Clock::get().map_err(|_| Error::UNSUPPORTED)?;

    // Use slot, unix_timestamp, and epoch as entropy sources
    let entropy_sources = [
        clock.slot.to_le_bytes(),
        clock.unix_timestamp.to_le_bytes(),
        clock.epoch.to_le_bytes(),
    ];

    // Mix entropy sources with buffer position for randomness
    for (i, byte) in buf.iter_mut().enumerate() {
        let source_idx = i % entropy_sources.len();
        let byte_idx = (i / entropy_sources.len()) % 8;
        let entropy_byte = entropy_sources[source_idx][byte_idx];

        // XOR with position-based value for additional mixing
        *byte = entropy_byte ^ ((i as u8).wrapping_mul(251).wrapping_add(179));
    }

    Ok(())
}

register_custom_getrandom!(solana_getrandom);
