"use client";

import { Provider } from "react-redux";
import { store } from "./store";

type ReducProviderProps = {
  children: React.ReactNode;
};

export default function ReduxProvider({ children }: ReducProviderProps) {
  return <Provider store={store}>{children}</Provider>;
}
