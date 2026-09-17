"use client";
import { useState } from "react";

import {
  useAddIncidentCommentMutation,
  useDeleteIncidentCommentMutation,
  useGetIncidentCommentsQuery,
  useUpdateIncidentCommentMutation,
} from "@/app/lib/services/api";
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
  const handleAddComment = async () => {
    const trimmedComment = comment.trim();

    if (!trimmedComment) {
      return;
    }

    try {
      await addIncidentComment({
        incidentId,
        content: trimmedComment,
      }).unwrap();
      setComment("");
    } catch (error) {
      console.error("Failed to add comment:", error);
    }
  };
  const handleEditComment = async (commentId: number) => {
    const content = editingContent.trim();
    if (!content) {
      return;
    }
    try {
      await updateIncidentComment({
        incidentId,
        commentId,
        content,
      }).unwrap();
      setEditingCommentId(null);
      setEditingContent("");
    } catch (error) {
      console.error("Failed to update comment:", error);
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
      await deleteIncidentComment({
        incidentId,
        commentId,
      }).unwrap();
    } catch (error) {
      console.error("Failed to delete comment:", error);
    }
  };

  return (
    <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-[var(--foreground)]">
          Comments
        </h2>

        <p className="mt-1 text-sm text-[var(--muted)]">
          Investigation discussion and incident updates.
        </p>
      </div>

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
              className="rounded-xl border border-[var(--border)] bg-black/5 p-4 dark:bg-white/5"
            >
              {editingCommentId === item.id ? (
                /* Edit mode */
                <div>
                  <textarea
                    value={editingContent}
                    onChange={(event) => setEditingContent(event.target.value)}
                    rows={4}
                    disabled={isUpdatingComment}
                    className="w-full rounded-lg border border-gray-200 bg-transparent px-3 py-2 text-sm text-gray-900 outline-none transition focus:border-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-800 dark:text-gray-100"
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
                      className="rounded-lg bg-[var(--accent)] px-3 py-1.5 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
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
          className="w-full rounded-xl border border-[var(--border)] bg-transparent px-4 py-3 text-sm text-[var(--foreground)] outline-none placeholder:text-[var(--muted)] focus:border-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-50"
        />

        <div className="mt-3 flex justify-end">
          <button
            type="button"
            onClick={() => void handleAddComment()}
            disabled={
              isAddingComment || !comment.trim() || editingCommentId !== null
            }
            className="rounded-lg bg-[var(--foreground)] px-4 py-2 text-sm font-semibold text-[var(--background)] transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isAddingComment ? "Adding..." : "Add comment"}
          </button>
        </div>
      </div>
    </section>
  );
}
