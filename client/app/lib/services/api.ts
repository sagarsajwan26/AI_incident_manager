import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

type RegisterRequest = {
  tenant_name: string;
  name: string;
  email: string;
  password: string;
};
type RegisterResponse = {
  id: number;
  tenant_id: number;
  name: string;
  email: string;
  role: string;
};

type LoginRequest = {
  email: string;
  password: string;
};
type LoginResponse = {
  access_token: string;
  token_type: string;
};

type MeResponse = {
  id: number;
  name: string;
  email: string;
};

type Investigation = {
  id: number;
  incident_id: number;
  tenant_id: number;
  provider: string;
  model: string;
  summary: string;
  likely_root_cause: string;
  root_cause_status: "confirmed" | "probable" | "unknown";
  evidence: string[];
  impact: string;
  recommended_actions: string[];
  unknowns: string[];
  confidence: number;
  created_at: string;
};
export type Incident = {
  tenant_id: number;
  id: number;
  title: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "investigating" | "contained" | "resolved" | "closed";
  reported_by: number;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
};

type Evidence = {
  id: number;
  incident_id: number;
  tenant_id: number;
  added_by: number;
  evidence_type: string;
  content: string;
  source: string | null;
  external_id: string | null;
  created_at: string;
};

type AddEvidenceRequest = {
  incidentId: number;
  evidence_type: string;
  content: string;
};

export type Comment = {
  id: number;
  incident_id: number;
  tenant_id: number;
  user_id: number;
  content: string;
  created_at: string;
  updated_at: string;
};
type AddCommentRequest = {
  incidentId: number;
  content: string;
};

type UpdateCommentRequest = {
  incidentId: number;
  commentId: number;
  content: string;
};

export type IncidentAudit = {
  id: number;
  incident_id: number;
  tenant_id: number;
  user_id: number;
  action: string;
  details: string | null;
  created_at: string;
};
export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
    credentials: "include",
  }),
  tagTypes: [
    "Auth",
    "InvestigationHistory",
    "Evidence",
    "Incident",
    "Comment",
    "Audit",
  ],
  endpoints: (builder) => ({
    register: builder.mutation<RegisterResponse, RegisterRequest>({
      query: (body) => ({
        url: "/api/v1/auth/register",
        method: "POST",
        body,
      }),
    }),

    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (body) => ({
        url: "/api/v1/auth/login",
        method: "POST",
        body,
      }),
    }),
    me: builder.query<MeResponse, void>({
      query: () => ({
        url: "/api/v1/auth/me",
        method: "GET",
      }),
      providesTags: ["Auth"],
    }),
    logout: builder.mutation<{ message: string }, void>({
      query: () => ({
        url: "/api/v1/auth/logout",
        method: "POST",
      }),
      invalidatesTags: ["Auth"],
    }),
    getIncidents: builder.query<Incident[], void>({
      query: () => ({
        url: "/api/v1/incidents/",
        method: "GET",
      }),
    }),
    getIncident: builder.query<Incident, number>({
      query: (incidentId) => ({
        url: `/api/v1/incidents/${incidentId}`,
        method: "GET",
      }),
      providesTags: (_result, _error, incidentId) => [
        { type: "Incident", id: incidentId },
      ],
    }),
    getIncidentEvidence: builder.query<Evidence[], number>({
      query: (incidentId) => ({
        url: `/api/v1/incidents/${incidentId}/evidence`,
        method: "GET",
      }),
      providesTags: (_result, _error, incidentId) => [
        { type: "Evidence", id: incidentId },
      ],
    }),

    investigateIncident: builder.mutation<Investigation, number>({
      query: (incidentId) => ({
        url: `/api/v1/incidents/${incidentId}/investigate`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, incidentId) => [
        { type: "InvestigationHistory", id: incidentId },
      ],
    }),
    getIncidentInvestigations: builder.query<Investigation[], number>({
      query: (incidentId) => `/api/v1/incidents/${incidentId}/investigations`,
      providesTags: (_result, _error, incidentId) => [
        { type: "InvestigationHistory", id: incidentId },
      ],
    }),

    getIncidentInvestigation: builder.query<
      Investigation,
      { incidentId: number; investigationId: number }
    >({
      query: ({ incidentId, investigationId }) =>
        `/api/v1/incidents/${incidentId}/investigations/${investigationId}`,
    }),

    addIncidentEvidence: builder.mutation<Evidence, AddEvidenceRequest>({
      query: ({ incidentId, evidence_type, content }) => ({
        url: `/api/v1/incidents/${incidentId}/evidence`,
        method: "POST",
        body: {
          evidence_type,
          content,
        },
      }),
      invalidatesTags: (_result, _error, { incidentId }) => [
        { type: "Evidence", id: incidentId },
      ],
    }),
    updateIncidentStatus: builder.mutation<
      Incident,
      {
        incidentId: number;
        status: Incident["status"];
      }
    >({
      query: ({ incidentId, status }) => ({
        url: `/api/v1/incidents/${incidentId}/status`,
        method: "PATCH",
        body: { status },
      }),
      invalidatesTags: (_result, _error, { incidentId }) => [
        { type: "Incident", id: incidentId },
      ],
    }),

    getIncidentComments: builder.query<Comment[], number>({
      query: (incidentId) => `/api/v1/incidents/${incidentId}/comments`,
      providesTags: (_result, _error, incidentId) => [
        { type: "Comment", id: incidentId },
      ],
    }),

    addIncidentComment: builder.mutation<Comment, AddCommentRequest>({
      query: ({ incidentId, content }) => ({
        url: `/api/v1/incidents/${incidentId}/comments`,
        method: "POST",
        body: {
          content,
        },
      }),
      invalidatesTags: (_result, _error, { incidentId }) => [
        { type: "Comment", id: incidentId },
      ],
    }),
    updateIncidentComment: builder.mutation<Comment, UpdateCommentRequest>({
      query: ({ incidentId, commentId, content }) => ({
        url: `/api/v1/incidents/${incidentId}/comments/${commentId}`,
        method: "PATCH",
        body: {
          content,
        },
      }),
      invalidatesTags: (_result, _error, { incidentId }) => [
        { type: "Comment", id: incidentId },
      ],
    }),

    getIncidentAudit: builder.query<IncidentAudit[], number>({
      query: (incidentId) => `/api/v1/incidents/${incidentId}/audit`,
      providesTags: (_result, _error, incidentId) => [
        { type: "Audit", id: incidentId },
      ],
    }),
  }),
});

export const {
  useRegisterMutation,
  useLoginMutation,
  useMeQuery,
  useLogoutMutation,
  useGetIncidentsQuery,
  useGetIncidentQuery,
  useGetIncidentEvidenceQuery,
  useInvestigateIncidentMutation,
  useGetIncidentInvestigationsQuery,
  useGetIncidentInvestigationQuery,
  useAddIncidentEvidenceMutation,
  useUpdateIncidentStatusMutation,
  useGetIncidentCommentsQuery,
  useAddIncidentCommentMutation,
  useUpdateIncidentCommentMutation,
  useGetIncidentAuditQuery,
} = api;
