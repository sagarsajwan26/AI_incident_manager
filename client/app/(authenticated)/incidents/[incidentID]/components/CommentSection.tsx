"use client";
import { useState } from "react";

import {
  useAddIncidentCommentMutation,
  useGetIncidentCommentsQuery,
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
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.02] p-6">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-white">Comments</h2>

        <p className="mt-1 text-sm text-gray-500">
          Investigation discussion and incident updates.
        </p>
      </div>

      <div className="space-y-4">
        {isLoadingComments ? (
          <p className="text-sm text-gray-500">Loading comments...</p>
        ) : comments.length === 0 ? (
          <p className="text-sm text-gray-500">No comments yet.</p>
        ) : (
          comments.map((item) => (
            <div
              key={item.id}
              className="rounded-xl border border-white/10 bg-gray-950/60 p-4"
            >
              <p className="text-sm leading-6 text-gray-300">{item.content}</p>

              <p className="mt-2 text-xs text-gray-500">
                {new Date(item.created_at).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>

      <div className="mt-6 border-t border-white/10 pt-5">
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="Add a comment..."
          rows={4}
          className="w-full rounded-xl border border-white/10 bg-gray-950 px-4 py-3 text-sm text-gray-200 outline-none placeholder:text-gray-600 focus:border-gray-600"
        />

        <div className="mt-3 flex justify-end">
          <button
            type="button"
            onClick={handleAddComment}
            disabled={isAddingComment || !comment.trim()}
            className="rounded-lg bg-white px-4 py-2 text-sm font-medium text-gray-900 transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isAddingComment ? "Adding..." : "Add comment"}
          </button>
        </div>
      </div>
    </section>
  );
}
