import { describe, it, expect } from 'vitest';

describe('App', () => {
  it('should pass basic sanity check', () => {
    expect(1 + 1).toBe(2);
  });

  it('should have correct app title', () => {
    expect('GasMap').toBeTruthy();
  });
});
