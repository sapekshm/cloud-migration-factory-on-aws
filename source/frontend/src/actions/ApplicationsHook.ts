// @ts-nocheck
/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  requestStarted,
  requestSuccessful,
  requestFailed,
  reducer, DataHook
} from '../resources/reducer';

import { useReducer, useEffect } from 'react';

import { Auth } from "@aws-amplify/auth";
import User from "../actions/user";

export const useMFApps: DataHook = () => {
  const [state, dispatch] = useReducer(reducer, {
    isLoading: true,
    data: [],
    error: null
  });


  function localDataRemoveItem(id) {
    return state.data.filter(function (entry) {
      return entry.app_id !== id;
    });
  }

  async function deleteApplications(deleteItems) {
    let apiUser = null;

    try {
      const session = await Auth.currentSession();
      apiUser = new User(session);
    } catch (e) {
      console.log(e);
    }

      for(let item in deleteItems) {
        try {
          await apiUser.deleteApp(deleteItems[item].app_id);
          const lUpdatedData = localDataRemoveItem(deleteItems[item].app_id);
          dispatch(requestSuccessful({data: lUpdatedData}));
        } catch (err) {
          //Error deleting application.
        }

      }
  }


  async function update() {
    const myAbortController = new AbortController();

    dispatch(requestStarted());

    try {

      const session = await Auth.currentSession();
      let apiUser = await new User(session);
      const response = await apiUser.getApps({ signal: myAbortController.signal });

      dispatch(requestSuccessful({data: response}));

    } catch (e) {
      if (e.message !== 'Request aborted') {
        console.error('Applications Hook', e);
      }
      dispatch(requestFailed({ error: e.message }));

      return () => {
        myAbortController.abort();
      };
    }

    return () => {
      myAbortController.abort();
    };
  };

  useEffect(() => {

    let cancelledRequest;

    (async () => {
      await update();
      if (cancelledRequest) return;
    })();

    return () => {
      cancelledRequest = true;
    };

  },[]);

  return [state , { update, deleteApplications }];
};
