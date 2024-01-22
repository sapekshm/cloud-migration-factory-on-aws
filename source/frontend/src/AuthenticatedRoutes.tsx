// @ts-nocheck
/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import { Route, Routes } from "react-router-dom";
import UserTableApps from "./containers/UserTableApps";
import UserServerTable from "./containers/UserTableServers";
import UserDatabaseTable from "./containers/UserTableDatabases";
import UserWaveTable from "./containers/UserTableWaves";
import UserAutomationJobs from "./containers/UserAutomationJobs";
import UserAutomationScripts from "./containers/UserAutomationScripts";
import UserDashboard from "./containers/UserDashboard";
import UserImport from "./containers/UserImport";
import UserExport from "./containers/UserExport";
import NotFound from "./containers/NotFound";
import Login from "./containers/Login";
import AdminPermissions from "./containers/AdminPermissions";
import AdminSchemaMgmt from "./containers/AdminSchemaMgmt"
import ChangePassword from "./containers/ChangePassword";
import CredentialManager from "./containers/CredentialManager";
import Secrets from "./containers/Secrets";

export default ({ childProps }) => {

  return (

    <Routes>
      <Route
        path="/"
        element={
            <UserDashboard {...childProps}/>
      }
      />
      <Route
        path="/applications"
        element={
            <UserTableApps {...childProps}/>
        }
      />
      <Route
        path="/applications/:id"
        element={
          <UserTableApps {...childProps}/>
        }
      />
      <Route
        path="/applications/add"
        element={
          <UserTableApps {...childProps}/>
        }
      />
      <Route
        path="/applications/edit/:id"
        element={
          <UserTableApps {...childProps}/>
        }
      />
      <Route
        path="/servers"
        element={
          <UserServerTable {...childProps}/>
        }
      />
      <Route
        path="/servers/:id"
        element={
          <UserServerTable {...childProps}/>
        }
      />
      <Route
        path="/servers/add"
        element={
          <UserServerTable {...childProps}/>
        }
      />
      <Route
        path="/servers/edit/:id"
        element={
          <UserServerTable {...childProps}/>
        }
      />
      <Route
        path="/waves"
        element={
          <UserWaveTable {...childProps}/>
        }
      />
      <Route
        path="/waves/:id"
        element={
          <UserWaveTable {...childProps}/>
        }
      />
      <Route
        path="/waves/add"
        element={
          <UserWaveTable {...childProps}/>
        }
      />
      <Route
        path="/waves/edit/:id"
        element={
          <UserWaveTable {...childProps}/>
        }
      />
      <Route
        path="/databases"
        element={
          <UserDatabaseTable {...childProps}/>
        }
      />
      <Route
        path="/databases/:id"
        element={
          <UserDatabaseTable {...childProps}/>
        }
      />
      <Route
        path="/databases/add"
        element={
          <UserDatabaseTable {...childProps}/>
        }
      />
      <Route
        path="/databases/edit/:id"
        element={
          <UserDatabaseTable {...childProps}/>
        }
      />
      <Route
        path="/import"
        element={
          <UserImport {...childProps}/>
        }
      />
      <Route
        path="/export"
        element={
          <UserExport {...childProps}/>
        }
      />
      <Route
        path="/secrets"
        element={
          <Secrets {...childProps}/>
        }
      />
      <Route
        path="/automation/jobs"
        element={
          <UserAutomationJobs {...childProps}/>
        }
      />
      <Route
        path="/automation/jobs/:id"
        element={
          <UserAutomationJobs {...childProps}/>
        }
      />
      <Route
        path="/automation/scripts"
        element={
          <UserAutomationScripts {...childProps}/>
        }
      />
      <Route
        path="/automation/scripts/add"
        element={
          <UserAutomationScripts {...childProps}/>
        }
      />
      <Route path="/login" exact render={(props) => (
        <Login {...props} props={childProps} />
      )} />
      <Route
        path="/change/pwd"
        element={
          <ChangePassword {...childProps}/>
        }
      />
      childProps.userGroups ?
      childProps.userGroups.includes('admin')
      ?(
      <Route
        path="/admin/policy"
        element={
          <AdminPermissions {...childProps}/>
        }
      />
      <Route
        path="/admin/attribute"
        element={
          <AdminSchemaMgmt {...childProps}/>
        }
      />
      <Route
        path="/admin/credential-manager"
        element={
          <CredentialManager {...childProps}/>
        }
      />
      { /* Finally, catch all unmatched routes */}
      <Route component={NotFound} />
    </Routes>)
};
