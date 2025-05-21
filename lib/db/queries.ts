import 'server-only';

import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { User as SupabaseUser } from '@supabase/supabase-js'; // To avoid naming conflict

import type {
  User,
  Suggestion,
  DBMessage,
  Chat,
  Vote, // Added Vote
  Stream, // Added Stream
  Document as DBDocument, // Added Document and aliased to DBDocument
} from './schema';
import type { ArtifactKind } from '@/components/artifact';
import { generateUUID } from '../utils';
import { generateHashedPassword } from './utils';
import type { VisibilityType } from '@/components/visibility-selector';
import { ChatSDKError } from '../errors';

// Initialize Supabase client
// biome-ignore lint:పీ Forbidden non-null assertion. Ensure these are set in your .env
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
// biome-ignore lint:పీ Forbidden non-null assertion. Ensure these are set in your .env
const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

const supabase: SupabaseClient = createClient(
  supabaseUrl,
  supabaseServiceRoleKey,
  {
    auth: {
      // It's generally recommended to set persistSession to false for server-side operations
      // if you are not managing user sessions with the Supabase client directly here.
      // For service_role key usage, session persistence is not typically relevant.
      persistSession: false,
      autoRefreshToken: false,
    },
  },
);

// Helper function to handle Supabase errors
function handleSupabaseError(error: any, context: string) {
  if (error) {
    console.error(`Supabase error in ${context}:`, error);
    throw new ChatSDKError(
      'bad_request:database',
      `Failed in ${context}: ${error.message}`,
    );
  }
}

// Data Mapping Helpers to convert Supabase snake_case to schema.ts camelCase
function mapToCamelCase(obj: any, mapping: Record<string, string>): any {
  if (!obj) return null;
  const res: Record<string, any> = {};
  for (const key in obj) {
    res[mapping[key] || key] = obj[key];
  }
  return res;
}

function mapRawUserToUser(raw: any): User {
  // User schema seems to have simple lowercase names already (id, email, password)
  // If there were snake_case fields, map them here.
  // For now, assuming direct mapping is okay based on schema.ts
  return raw as User;
}

function mapRawChatToChat(raw: any): Chat {
  if (!raw) return null as unknown as Chat; // Ensure null returns propagate correctly
  return {
    id: raw.id,
    createdAt: raw.created_at || raw.createdAt, // Prioritize snake_case
    title: raw.title,
    userId: raw.user_id || raw.userId,
    visibility: raw.visibility,
  } as Chat;
}

function mapRawDbMessageToDbMessage(raw: any): DBMessage {
  if (!raw) return null as unknown as DBMessage;
  return {
    id: raw.id,
    chatId: raw.chat_id || raw.chatId,
    role: raw.role,
    parts: raw.parts, // Assuming 'parts' is fine as is or JSON
    attachments: raw.attachments, // Assuming 'attachments' is fine
    createdAt: raw.created_at || raw.createdAt,
  } as DBMessage;
}

function mapRawVoteToVote(raw: any): Vote {
  if (!raw) return null as unknown as Vote;
  return {
    chatId: raw.chat_id || raw.chatId,
    messageId: raw.message_id || raw.messageId,
    isUpvoted: raw.is_upvoted !== undefined ? raw.is_upvoted : raw.isUpvoted,
  } as Vote;
}

function mapRawDocumentToDocument(raw: any): DBDocument {
  if (!raw) return null as unknown as DBDocument;
  return {
    id: raw.id,
    createdAt: raw.created_at || raw.createdAt,
    title: raw.title,
    content: raw.content,
    kind: raw.kind,
    userId: raw.user_id || raw.userId,
  } as DBDocument;
}

function mapRawSuggestionToSuggestion(raw: any): Suggestion {
  if (!raw) return null as unknown as Suggestion;
  return {
    id: raw.id,
    documentId: raw.document_id || raw.documentId,
    documentCreatedAt: raw.document_created_at || raw.documentCreatedAt,
    originalText: raw.original_text || raw.originalText,
    suggestedText: raw.suggested_text || raw.suggestedText,
    description: raw.description,
    isResolved:
      raw.is_resolved !== undefined ? raw.is_resolved : raw.isResolved,
    userId: raw.user_id || raw.userId,
    createdAt: raw.created_at || raw.createdAt,
  } as Suggestion;
}

function mapRawStreamToStream(raw: any): Stream {
  if (!raw) return null as unknown as Stream;
  return {
    id: raw.id,
    chatId: raw.chat_id || raw.chatId,
    createdAt: raw.created_at || raw.createdAt,
  } as Stream;
}

export async function getUser(email: string): Promise<Array<User>> {
  try {
    const { data: rawData, error } = await supabase
      .from('user') // Assuming your table is named 'user'
      .select('*')
      .eq('email', email);

    handleSupabaseError(error, 'getUser by email');
    if (!rawData) return [];
    return rawData.map(mapRawUserToUser);
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get user by email: ${(error as Error).message}`,
    );
  }
}

export async function createUser(
  email: string,
  password: string,
): Promise<User | null> {
  const hashedPassword = generateHashedPassword(password);

  try {
    const { data: rawData, error } = await supabase
      .from('user')
      .insert([{ email, password: hashedPassword }])
      .select()
      .single(); // Assuming you want to return the created user

    handleSupabaseError(error, 'createUser');
    return rawData ? mapRawUserToUser(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to create user: ${(error as Error).message}`,
    );
  }
}

export async function createGuestUser(): Promise<Partial<User>> {
  const email = `guest-${Date.now()}@example.com`;
  const password = generateHashedPassword(generateUUID());

  try {
    const { data: rawData, error } = await supabase
      .from('user')
      .insert([{ email, password }])
      .select('id, email')
      .single();

    handleSupabaseError(error, 'createGuestUser');
    if (!rawData) throw new Error('Guest user creation returned no data');
    // rawData is { id: string, email: string }. This matches Partial<User> for these fields.
    return rawData; // No complex mapping needed here since selecting specific simple fields
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to create guest user: ${(error as Error).message}`,
    );
  }
}

export async function saveChat({
  id,
  userId,
  title,
  visibility,
}: {
  id: string;
  userId: string;
  title: string;
  visibility: VisibilityType;
}): Promise<Chat | null> {
  try {
    const { data: rawData, error } = await supabase
      .from('chat')
      .insert([
        {
          id,
          user_id: userId,
          title,
          visibility,
          created_at: new Date().toISOString(),
        },
      ])
      .select()
      .single();

    handleSupabaseError(error, 'saveChat');
    return rawData ? mapRawChatToChat(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to save chat: ${(error as Error).message}`,
    );
  }
}

export async function deleteChatById({
  id,
}: { id: string }): Promise<Chat | null> {
  try {
    // Supabase doesn't directly support cascading deletes in the client like Drizzle transaction
    // You'd need to handle related deletions (votes, messages, streams) separately or set up CASCADE in DB
    // For simplicity, this example only deletes the chat.
    // Consider using a Supabase Edge Function (database function) for complex transactional deletes.

    // Delete related items first (example for messages, adapt for votes, streams)
    const { error: messageError } = await supabase
      .from('message')
      .delete()
      .eq('chat_id', id);
    handleSupabaseError(messageError, 'deleteChatById (messages)');

    const { error: voteError } = await supabase
      .from('vote')
      .delete()
      .eq('chat_id', id);
    handleSupabaseError(voteError, 'deleteChatById (votes)');

    const { error: streamError } = await supabase
      .from('stream')
      .delete()
      .eq('chat_id', id);
    handleSupabaseError(streamError, 'deleteChatById (streams)');

    const { data: rawData, error: chatError } = await supabase
      .from('chat')
      .delete()
      .eq('id', id)
      .select()
      .single();

    handleSupabaseError(chatError, 'deleteChatById (chat)');
    return rawData ? mapRawChatToChat(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to delete chat by id: ${(error as Error).message}`,
    );
  }
}

export async function getChatsByUserId({
  id,
  limit,
  startingAfter, // This needs re-thinking with Supabase cursors or offset/limit
  endingBefore, // This needs re-thinking with Supabase cursors or offset/limit
}: {
  id: string;
  limit: number;
  startingAfter: string | null;
  endingBefore: string | null;
}): Promise<{ chats: Array<Chat>; hasMore: boolean }> {
  // Basic pagination example (offset-based).
  // For cursor-based pagination with Supabase, you'd typically use range() and order by a unique, sequential column.
  // The original logic with startingAfter/endingBefore based on createdAt might be complex to replicate directly
  // without knowing the exact Supabase query patterns you'd prefer.
  // This simplified version uses offset pagination.

  const offset = 0;
  // If you had a way to translate startingAfter/endingBefore to an offset, it would go here.
  // This is a placeholder for a more sophisticated pagination.
  // For now, we'll ignore startingAfter and endingBefore for this simplified Supabase conversion.

  try {
    const {
      data: rawData,
      error,
      count,
    } = await supabase
      .from('chat')
      .select('*', { count: 'exact' })
      .eq('user_id', id)
      .order('created_at', { ascending: false })
      .limit(limit)
      .range(offset, offset + limit - 1); // Simple offset pagination

    handleSupabaseError(error, 'getChatsByUserId');

    const chats = rawData ? rawData.map(mapRawChatToChat) : [];
    const totalCount = count || 0;
    const hasMore = offset + chats.length < totalCount;

    return {
      chats,
      hasMore,
    };
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get chats by user id: ${(error as Error).message}`,
    );
  }
}

export async function getChatById({
  id,
}: { id: string }): Promise<Chat | null> {
  try {
    const { data: rawData, error } = await supabase
      .from('chat')
      .select('*')
      .eq('id', id)
      .maybeSingle(); // Use maybeSingle to return null if not found, instead of error

    handleSupabaseError(error, 'getChatById');
    return rawData ? mapRawChatToChat(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get chat by id: ${(error as Error).message}`,
    );
  }
}

export async function saveMessages({
  messages,
}: {
  messages: Array<DBMessage>;
}): Promise<Array<DBMessage> | null> {
  // Ensure column names match your Supabase table (e.g., chat_id, created_at)
  const messagesToInsert = messages.map((m) => ({
    // Map DBMessage (camelCase from input) to snake_case for Supabase insert
    id: m.id, // Assuming id is provided or auto-generated by DB and not needed in insert if so
    chat_id: m.chatId,
    role: m.role,
    parts: m.parts,
    attachments: m.attachments,
    created_at: m.createdAt
      ? new Date(m.createdAt).toISOString()
      : new Date().toISOString(),
  }));

  try {
    const { data: rawData, error } = await supabase
      .from('message')
      .insert(messagesToInsert)
      .select();

    handleSupabaseError(error, 'saveMessages');
    return rawData ? rawData.map(mapRawDbMessageToDbMessage) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to save messages: ${(error as Error).message}`,
    );
  }
}

export async function getMessagesByChatId({
  id,
}: { id: string }): Promise<Array<DBMessage>> {
  try {
    const { data: rawData, error } = await supabase
      .from('message')
      .select('*')
      .eq('chat_id', id) // Assuming column is chat_id
      .order('created_at', { ascending: true }); // Assuming column is created_at

    handleSupabaseError(error, 'getMessagesByChatId');
    return rawData ? rawData.map(mapRawDbMessageToDbMessage) : [];
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get messages by chat id: ${(error as Error).message}`,
    );
  }
}

export async function voteMessage({
  chatId,
  messageId,
  type,
}: {
  chatId: string;
  messageId: string;
  type: 'up' | 'down';
}): Promise<Vote | null> {
  // Return type might change based on Supabase response
  try {
    // Upsert logic for votes
    const { data: rawData, error } = await supabase
      .from('vote')
      .upsert(
        {
          chat_id: chatId, // Assuming schema uses snake_case
          message_id: messageId,
          is_upvoted: type === 'up',
        },
        {
          onConflict: 'chat_id, message_id', // Specify conflict target
        },
      )
      .select()
      .single();

    handleSupabaseError(error, 'voteMessage');
    return rawData ? mapRawVoteToVote(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to vote message: ${(error as Error).message}`,
    );
  }
}

export async function getVotesByChatId({
  id,
}: { id: string }): Promise<Array<Vote>> {
  // Adjust 'any'
  try {
    const { data: rawData, error } = await supabase
      .from('vote')
      .select('*')
      .eq('chat_id', id);

    handleSupabaseError(error, 'getVotesByChatId');
    return rawData ? rawData.map(mapRawVoteToVote) : [];
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get votes by chat id: ${(error as Error).message}`,
    );
  }
}

export async function saveDocument({
  id,
  title,
  kind,
  content,
  userId,
}: {
  id: string;
  title: string;
  kind: ArtifactKind;
  content: string;
  userId: string;
}): Promise<DBDocument | null> {
  try {
    const { data: rawData, error } = await supabase
      .from('document')
      .insert([
        {
          id,
          title,
          kind,
          content,
          user_id: userId,
          created_at: new Date().toISOString(),
        },
      ])
      .select()
      .single();

    handleSupabaseError(error, 'saveDocument');
    return rawData ? mapRawDocumentToDocument(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to save document: ${(error as Error).message}`,
    );
  }
}

export async function getDocumentById({
  id,
}: { id: string }): Promise<DBDocument | null> {
  try {
    const { data: rawData, error } = await supabase
      .from('document')
      .select('*')
      .eq('id', id)
      // .order('created_at', { ascending: false }) // original was desc
      .maybeSingle(); // If you expect one or null

    handleSupabaseError(error, 'getDocumentById');
    return rawData ? mapRawDocumentToDocument(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get document by id: ${(error as Error).message}`,
    );
  }
}

// getDocumentsById was similar to getDocumentById but returned an array
// If this distinction is important, it needs to be implemented.
// For now, I'm providing one getDocumentById which can be adapted.
// The original getDocumentsById ordered by asc(createdAt)

export async function deleteDocumentsByIdAfterTimestamp({
  id,
  timestamp,
}: {
  id: string;
  timestamp: Date;
}): Promise<DBDocument[] | null> {
  // Adjust 'any'
  try {
    // Delete related suggestions first
    const { error: suggestionError } = await supabase
      .from('suggestion')
      .delete()
      .eq('document_id', id)
      .gt('document_created_at', timestamp.toISOString()); // Ensure column name matches
    handleSupabaseError(
      suggestionError,
      'deleteDocumentsByIdAfterTimestamp (suggestions)',
    );

    const { data: rawData, error: documentError } = await supabase
      .from('document')
      .delete()
      .eq('id', id)
      .gt('created_at', timestamp.toISOString())
      .select(); // To get returning data

    handleSupabaseError(
      documentError,
      'deleteDocumentsByIdAfterTimestamp (documents)',
    );
    return rawData ? rawData.map(mapRawDocumentToDocument) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to delete documents by id after timestamp: ${(error as Error).message}`,
    );
  }
}

export async function saveSuggestions({
  suggestions,
}: {
  suggestions: Array<Suggestion>; // Assuming Suggestion type is compatible or adapted
}): Promise<Array<Suggestion> | null> {
  // Adapt suggestions structure if necessary for Supabase (e.g. column names)
  const suggestionsToInsert = suggestions.map((s) => ({
    // Map Suggestion (camelCase from input) to snake_case for Supabase insert
    id: s.id, // Assuming id is provided or auto-generated by DB
    document_id: s.documentId,
    document_created_at: s.documentCreatedAt
      ? new Date(s.documentCreatedAt).toISOString()
      : undefined, // Handle Date object
    original_text: s.originalText,
    suggested_text: s.suggestedText,
    description: s.description,
    is_resolved: s.isResolved,
    user_id: s.userId,
    created_at: s.createdAt
      ? new Date(s.createdAt).toISOString()
      : new Date().toISOString(),
  }));
  try {
    const { data: rawData, error } = await supabase
      .from('suggestion')
      .insert(suggestionsToInsert)
      .select();

    handleSupabaseError(error, 'saveSuggestions');
    return rawData ? rawData.map(mapRawSuggestionToSuggestion) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to save suggestions: ${(error as Error).message}`,
    );
  }
}

export async function getSuggestionsByDocumentId({
  documentId,
}: {
  documentId: string;
}): Promise<Array<Suggestion>> {
  try {
    const { data: rawData, error } = await supabase
      .from('suggestion')
      .select('*')
      .eq('document_id', documentId); // Assuming column name

    handleSupabaseError(error, 'getSuggestionsByDocumentId');
    return rawData ? rawData.map(mapRawSuggestionToSuggestion) : [];
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get suggestions by document id: ${(error as Error).message}`,
    );
  }
}

export async function getMessageById({
  id,
}: { id: string }): Promise<DBMessage | null> {
  try {
    const { data: rawData, error } = await supabase
      .from('message')
      .select('*')
      .eq('id', id)
      .maybeSingle();

    handleSupabaseError(error, 'getMessageById');
    return rawData ? mapRawDbMessageToDbMessage(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get message by id: ${(error as Error).message}`,
    );
  }
}

export async function deleteMessagesByChatIdAfterTimestamp({
  chatId,
  timestamp,
}: {
  chatId: string;
  timestamp: Date;
}): Promise<DBMessage[] | null> {
  // Adjust 'any'
  try {
    // First, get IDs of messages to delete to handle related votes
    const { data: messagesToDelete, error: selectError } = await supabase
      .from('message')
      .select('id')
      .eq('chat_id', chatId)
      .gte('created_at', timestamp.toISOString());

    handleSupabaseError(
      selectError,
      'deleteMessagesByChatIdAfterTimestamp (select messages)',
    );

    if (messagesToDelete && messagesToDelete.length > 0) {
      const messageIds = messagesToDelete.map((m: { id: string }) => m.id);

      // Delete related votes
      const { error: voteError } = await supabase
        .from('vote')
        .delete()
        .eq('chat_id', chatId)
        .in('message_id', messageIds);
      handleSupabaseError(
        voteError,
        'deleteMessagesByChatIdAfterTimestamp (votes)',
      );

      // Delete messages
      const { data: rawData, error: messageError } = await supabase
        .from('message')
        .delete()
        .in('id', messageIds)
        .select();
      handleSupabaseError(
        messageError,
        'deleteMessagesByChatIdAfterTimestamp (messages)',
      );
      return rawData ? rawData.map(mapRawDbMessageToDbMessage) : null;
    }
    return [];
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to delete messages by chat id after timestamp: ${(error as Error).message}`,
    );
  }
}

export async function updateChatVisiblityById({
  chatId,
  visibility,
}: {
  chatId: string;
  visibility: 'private' | 'public';
}): Promise<Chat | null> {
  // Adjust 'any'
  try {
    const { data: rawData, error } = await supabase
      .from('chat')
      .update({ visibility })
      .eq('id', chatId)
      .select()
      .single();

    handleSupabaseError(error, 'updateChatVisibilityById');
    return rawData ? mapRawChatToChat(rawData) : null;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to update chat visibility by id: ${(error as Error).message}`,
    );
  }
}

export async function getMessageCountByUserId({
  id,
  differenceInHours,
}: { id: string; differenceInHours: number }): Promise<number> {
  try {
    const targetDate = new Date(
      Date.now() - differenceInHours * 60 * 60 * 1000,
    ).toISOString();

    // This is a bit more complex with Supabase client if it involves joins for count.
    // A Supabase Edge Function (db function) might be simpler for complex aggregates.
    // Or, a view.
    // Simplified: count messages directly associated with user, then filter by role client-side or in a more complex query
    // This example counts messages linked to chats owned by the user.

    // Get user's chats
    const { data: chats, error: chatsError } = await supabase
      .from('chat')
      .select('id')
      .eq('user_id', id);
    handleSupabaseError(chatsError, 'getMessageCountByUserId (get chats)');

    if (!chats || chats.length === 0) {
      return 0;
    }
    const chatIds = chats.map((c) => c.id);

    const { count, error: messagesError } = await supabase
      .from('message')
      .select('*', { count: 'exact', head: true }) // head: true for count only
      .in('chat_id', chatIds)
      .gte('created_at', targetDate)
      .eq('role', 'user'); // Assuming 'role' column exists

    handleSupabaseError(
      messagesError,
      'getMessageCountByUserId (count messages)',
    );
    return count || 0;
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get message count by user id: ${(error as Error).message}`,
    );
  }
}

// Functions for 'stream' table
export async function createStreamId({
  streamId,
  chatId,
}: {
  streamId: string;
  chatId: string;
}): Promise<void> {
  try {
    const { error } = await supabase
      .from('stream') // Assuming table name is 'stream'
      .insert([
        { id: streamId, chat_id: chatId, created_at: new Date().toISOString() },
      ]);

    handleSupabaseError(error, 'createStreamId');
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to create stream id: ${(error as Error).message}`,
    );
  }
}

export async function getStreamIdsByChatId({
  chatId,
}: { chatId: string }): Promise<string[]> {
  try {
    const { data, error } = await supabase
      .from('stream')
      .select('id')
      .eq('chat_id', chatId)
      .order('created_at', { ascending: true });

    handleSupabaseError(error, 'getStreamIdsByChatId');
    return data ? data.map((s: { id: string }) => s.id) : [];
  } catch (error) {
    if (error instanceof ChatSDKError) throw error;
    throw new ChatSDKError(
      'bad_request:database',
      `Failed to get stream ids by chat id: ${(error as Error).message}`,
    );
  }
}

// Note: The types User, Suggestion, DBMessage, Chat from './schema' might need adjustment
// if their structure was tightly coupled to Drizzle. Supabase results will be plain objects.
// You might need to update these type definitions or use Supabase's generated types if you generate them.
// For now, I've assumed they are structurally compatible or will be adjusted by you.
// Also, ensure all table and column names (e.g., 'user', 'chat_id', 'created_at') match your Supabase schema exactly.
// Snake_case is common in Supabase (e.g. user_id, created_at).
