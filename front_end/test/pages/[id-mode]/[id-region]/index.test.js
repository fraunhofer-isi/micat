import Index from '../../../../src/pages/[id-mode]/[id-region]/index';

it('construction', () => {
  const result = Index({});
  expect(result).toBe('Hello world');
});
