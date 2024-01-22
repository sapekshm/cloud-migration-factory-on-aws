// @ts-nocheck


/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

// IntakeFormTable.test
import {cleanup, screen, render} from '@testing-library/react';
import IntakeFormTable from "./IntakeFormTable";

afterEach(cleanup);

test('IntakeFormTable displays the empty items table with header Import', () => {
  render(
    <IntakeFormTable
      schema={[]}
      items={[]}
      isLoading={false}
      errorLoading={null}
    />,
  );

  expect(screen.getByText('Import')).toBeTruthy();

});