"use client";
import { useState } from "react";

import {
  useAddIncidentCommentMutation,
  useDeleteIncidentCommentMutation,
  useGetIncidentCommentsQuery,
  useUpdateIncidentCommentMutation,
} from "@/app/lib/services/api";
import { getApiErrorMessage } from "@/app/lib/utils/apiError";
type CommentsSectionProps = {
  incidentId: number;
};

export default function CommentsSection({ incidentId }: CommentsSectionProps) {
  const { data: comments = [], isLoading: isLoadingComments } =
    useGetIncidentCommentsQuery(incidentId);

  const [addIncidentComment, { isLoading: isAddingComment }] =
    useAddIncidentCommentMutation();

  const [comment, setComment] = useState("");
  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState("");
  const [deleteIncidentComment, { isLoading: isDeletingComment }] =
    useDeleteIncidentCommentMutation();
  const [updateIncidentComment, { isLoading: isUpdatingComment }] =
    useUpdateIncidentCommentMutation();

  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleAddComment = async () => {
    const trimmedComment = comment.trim();

    if (!trimmedComment) {
      return;
    }

    try {
      setErrorMsg(null);
      await addIncidentComment({
        incidentId,
        content: trimmedComment,
      }).unwrap();
      setComment("");
    } catch (error) {
      setErrorMsg(getApiErrorMessage(error));
    }
  };
  const handleEditComment = async (commentId: number) => {
    const content = editingContent.trim();
    if (!content) {
      return;
    }
    try {
      setErrorMsg(null);
      await updateIncidentComment({
        incidentId,
        commentId,
        content,
      }).unwrap();
      setEditingCommentId(null);
      setEditingContent("");
    } catch (error) {
      setErrorMsg(getApiErrorMessage(error));
    }
  };
  const handleDeleteComment = async (commentId: number) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?",
    );
    if (!confirmed) {
      return;
    }

    try {
      setErrorMsg(null);
      await deleteIncidentComment({
        incidentId,
        commentId,
      }).unwrap();
    } catch (error) {
      setErrorMsg(getApiErrorMessage(error));
    }
  };

  return (
    <section className="rounded-2xl glass-panel p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-[var(--foreground)]">
          Comments
        </h2>

        <p className="mt-1 text-sm text-[var(--muted)]">
          Investigation discussion and incident updates.
        </p>
      </div>

      {errorMsg && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="text-sm text-red-600">{errorMsg}</p>
        </div>
      )}

      {/* Comments list */}
      <div className="space-y-4">
        {isLoadingComments ? (
          <p className="text-sm text-[var(--muted)]">Loading comments...</p>
        ) : comments.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">No comments yet.</p>
        ) : (
          comments.map((item) => (
            <article
              key={item.id}
              className="rounded-xl border border-transparent bg-black/5 p-4 dark:bg-white/5"
            >
              {editingCommentId === item.id ? (
                /* Edit mode */
                <div>
                    <textarea
                      value={editingContent}
                      onChange={(event) => setEditingContent(event.target.value)}
                      rows={4}
                      disabled={isUpdatingComment}
                      className="w-full rounded-lg border border-transparent bg-black/5 px-3 py-2 text-sm text-black outline-none transition focus:border-gray-300 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white/5 dark:text-white dark:focus:border-gray-700"
                    />

                  <div className="mt-3 flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setEditingCommentId(null);
                        setEditingContent("");
                      }}
                      disabled={isUpdatingComment}
                      className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm font-medium text-[var(--foreground)] transition hover:bg-black/5 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-white/5"
                    >
                      Cancel
                    </button>

                    <button
                      type="button"
                      onClick={() => void handleEditComment(item.id)}
                      disabled={isUpdatingComment || !editingContent.trim()}
                      className="rounded-full bg-black px-4 py-1.5 text-sm font-semibold text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black"
                    >
                      {isUpdatingComment ? "Saving..." : "Save"}
                    </button>
                  </div>
                </div>
              ) : (
                /* View mode */
                <>
                  <p className="whitespace-pre-wrap text-sm leading-6 text-[var(--foreground)]">
                    {item.content}
                  </p>

                  <div className="mt-3 flex items-center justify-between gap-4">
                    <p className="text-xs text-[var(--muted)]">
                      {new Date(item.created_at).toLocaleString()}
                    </p>

                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => {
                          setEditingCommentId(item.id);
                          setEditingContent(item.content);
                        }}
                        className="text-xs font-medium text-[var(--accent)] hover:underline"
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        onClick={() => void handleDeleteComment(item.id)}
                        disabled={isDeletingComment}
                        className="text-xs font-medium text-red-500 hover:underline disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isDeletingComment ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </div>
                </>
              )}
            </article>
          ))
        )}
      </div>

      {/* Add comment */}
      <div className="mt-6 border-t border-[var(--border)] pt-5">
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="Add a comment..."
          rows={4}
          disabled={isAddingComment}
          className="w-full rounded-xl border border-transparent bg-black/5 px-4 py-3 text-sm text-black outline-none transition placeholder:text-gray-400 focus:border-gray-300 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white/5 dark:text-white dark:focus:border-gray-700"
        />

        <div className="mt-3 flex justify-end">
          <button
            type="button"
            onClick={() => void handleAddComment()}
            disabled={
              isAddingComment || !comment.trim() || editingCommentId !== null
            }
            className="rounded-full bg-black px-6 py-2.5 text-sm font-semibold text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black"
          >
            {isAddingComment ? "Adding..." : "Add comment"}
          </button>
        </div>
      </div>
    </section>
  );
}
