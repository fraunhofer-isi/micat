// © 2023 - 2024 Fraunhofer-Gesellschaft e.V., München
//
// SPDX-License-Identifier: AGPL-3.0-or-later

import Index from '../../../../src/pages/[id-mode]/[id-region]/index';

it('construction', () => {
  const result = Index({});
  expect(result).toBe('Hello world');
});
