"use client";
import React from "react";
export const Topbar = () => {
  return (
    <header className="h-16 glass-panel flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center gap-4">
        {/* Breadcrumb or search can go here */}
        <div className="relative group hidden sm:block">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <svg className="w-4 h-4 text-gray-400 group-focus-within:text-black dark:group-focus-within:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
          <input type="text" className="bg-black/5 dark:bg-white/5 border border-transparent text-sm rounded-full focus:ring-0 focus:border-gray-300 dark:focus:border-gray-700 block w-64 pl-10 p-2 placeholder-gray-400 text-black dark:text-white transition-all outline-none shadow-sm" placeholder="Search incidents..." />
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-gray-500 hover:text-black dark:hover:text-white transition-colors rounded-full hover:bg-black/5 dark:hover:bg-white/5">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-black"></span>
        </button>
        
        <div className="h-8 w-8 rounded-full bg-gray-100 dark:bg-gray-800 cursor-pointer flex items-center justify-center transition-transform hover:scale-105">
          <span className="text-xs font-semibold text-black dark:text-white">JD</span>
        </div>
      </div>
    </header>
  );
};
