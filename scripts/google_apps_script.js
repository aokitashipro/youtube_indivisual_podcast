/**
 * YouTube AI Podcast - Google Apps Script
 * 
 * このスクリプトは以下の機能を提供します：
 * 1. 新しい実行ログ行の自動作成
 * 2. メタデータとサムネイルの管理
 * 3. 統計情報の自動計算
 * 4. データ検証とエラーチェック
 * 
 * 列構成（v2.0 - メタデータ・サムネイル対応）:
 * A: 実行日時
 * B: タイトル
 * C: 説明文（最初の500文字）
 * D: タグ
 * E: サムネイルテキスト
 * F: コメント（毒舌設定）
 * G: 動画パス
 * H: 音声パス
 * I: サムネイルパス
 * J: 処理時間
 * K: ステータス
 * L: 動画URL（Drive）
 * M: 音声URL（Drive）
 * N: サムネイルURL（Drive）
 */

// ============================================================================
// 設定
// ============================================================================

const CONFIG = {
  MAIN_SHEET_NAME: '動画生成ログ',
  STATS_SHEET_NAME: '統計情報',
  TIMEZONE: 'Asia/Tokyo',
  // 列インデックス
  COL: {
    EXECUTION_TIME: 1,   // A
    TITLE: 2,            // B
    DESCRIPTION: 3,      // C
    TAGS: 4,             // D
    THUMBNAIL_TEXT: 5,   // E
    COMMENT: 6,          // F
    VIDEO_PATH: 7,       // G
    AUDIO_PATH: 8,       // H
    THUMBNAIL_PATH: 9,   // I
    PROCESSING_TIME: 10, // J
    STATUS: 11,          // K
    VIDEO_URL: 12,       // L
    AUDIO_URL: 13,       // M
    THUMBNAIL_URL: 14    // N
  }
};

// ============================================================================
// メニュー追加
// ============================================================================

/**
 * スプレッドシート起動時にカスタムメニューを追加
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🎬 YouTube AI Podcast')
    .addItem('📝 新しい実行ログを作成', 'createNewExecutionLog')
    .addSeparator()
    .addItem('📊 統計情報を更新', 'updateStatistics')
    .addItem('🎨 サムネイルテキスト一覧', 'showThumbnailTexts')
    .addSeparator()
    .addItem('✅ データ検証', 'validateData')
    .addItem('🧹 古いログをアーカイブ', 'archiveOldLogs')
    .addToUi();
}

// ============================================================================
// 実行ログ管理
// ============================================================================

/**
 * 新しい実行ログ行を作成（v2.0 - メタデータ対応）
 */
function createNewExecutionLog() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('エラー: 「実行ログ」シートが見つかりません');
    return;
  }
  
  // ヘッダーが存在しない場合は作成
  if (sheet.getLastRow() === 0) {
    initializeSheet(sheet);
  }
  
  // 実行日時
  const now = new Date();
  const timestamp = Utilities.formatDate(now, CONFIG.TIMEZONE, 'yyyy-MM-dd HH:mm:ss');
  
  // 新しい行を追加（v2.0構造）
  const newRow = [
    timestamp,      // A: 実行日時
    '',             // B: タイトル
    '',             // C: 説明文
    '',             // D: タグ
    '',             // E: サムネイルテキスト
    '',             // F: コメント
    '',             // G: 動画パス
    '',             // H: 音声パス
    '',             // I: サムネイルパス
    '',             // J: 処理時間
    '処理中',       // K: ステータス
    '',             // L: 動画URL
    '',             // M: 音声URL
    ''              // N: サムネイルURL
  ];
  
  sheet.appendRow(newRow);
  
  // セルの書式設定
  const lastRowNum = sheet.getLastRow();
  sheet.getRange(lastRowNum, CONFIG.COL.STATUS).setBackground('#fff4cc'); // ステータスを黄色に
  
  SpreadsheetApp.getUi().alert(`✅ 新しい実行ログを作成しました\n行番号: ${lastRowNum}`);
  
  Logger.log(`新しい実行ログを作成: 行${lastRowNum}`);
  
  return lastRowNum;
}

/**
 * シートを初期化（ヘッダーを作成）
 */
function initializeSheet(sheet) {
  const headers = [
    '実行日時',
    'タイトル',
    '説明文',
    'タグ',
    'サムネイルテキスト',
    'コメント',
    '動画パス',
    '音声パス',
    'サムネイルパス',
    '処理時間',
    'ステータス',
    '動画URL',
    '音声URL',
    'サムネイルURL'
  ];
  
  sheet.appendRow(headers);
  
  // ヘッダーの書式設定
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setFontWeight('bold')
    .setBackground('#4a86e8')
    .setFontColor('#ffffff')
    .setHorizontalAlignment('center');
  
  // 列幅を自動調整
  sheet.autoResizeColumns(1, headers.length);
  
  Logger.log('シートを初期化しました');
}

/**
 * サムネイルテキスト一覧を表示
 */
function showThumbnailTexts() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('エラー: 「実行ログ」シートが見つかりません');
    return;
  }
  
  const data = sheet.getDataRange().getValues();
  const thumbnails = [];
  
  for (let i = 1; i < data.length; i++) {
    const timestamp = data[i][CONFIG.COL.EXECUTION_TIME - 1];
    const thumbnailText = data[i][CONFIG.COL.THUMBNAIL_TEXT - 1];
    const status = data[i][CONFIG.COL.STATUS - 1];
    
    if (thumbnailText && status === '完了') {
      thumbnails.push(`${i + 1}行目: ${thumbnailText} (${timestamp})`);
    }
  }
  
  if (thumbnails.length === 0) {
    SpreadsheetApp.getUi().alert('サムネイルテキストが見つかりません');
  } else {
    const message = `📋 サムネイルテキスト一覧 (${thumbnails.length}件):\n\n` + thumbnails.slice(0, 10).join('\n');
    SpreadsheetApp.getUi().alert(message);
  }
}

/**
 * 実行ログのステータスを更新
 */
function updateExecutionStatus(executionId, status, notes = '') {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
  
  if (!sheet) return false;
  
  const data = sheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === executionId) {
      sheet.getRange(i + 1, 3).setValue(status); // C列: ステータス
      
      // ステータスに応じて背景色を変更
      if (status === '完了') {
        sheet.getRange(i + 1, 3).setBackground('#d9ead3');
      } else if (status === 'エラー') {
        sheet.getRange(i + 1, 3).setBackground('#f4cccc');
      }
      
      // 備考を追加
      if (notes) {
        sheet.getRange(i + 1, 11).setValue(notes); // K列: 備考
      }
      
      Logger.log(`ステータスを更新: ${executionId} -> ${status}`);
      return true;
    }
  }
  
  return false;
}

// ============================================================================
// プロンプト管理
// ============================================================================

/**
 * 実行ステータスを更新
 */
function updateExecutionStatus(rowNumber, status, notes = '') {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
  
  if (!sheet) return false;
  
  sheet.getRange(rowNumber, CONFIG.COL.STATUS).setValue(status);
  
  // ステータスに応じて背景色を変更
  if (status === '完了') {
    sheet.getRange(rowNumber, CONFIG.COL.STATUS).setBackground('#d9ead3');
  } else if (status === 'エラー') {
    sheet.getRange(rowNumber, CONFIG.COL.STATUS).setBackground('#f4cccc');
  }
  
  // 備考を追加（ステータス列の隣）
  if (notes) {
    sheet.getRange(rowNumber, CONFIG.COL.STATUS + 1).setValue(notes);
  }
  
  Logger.log(`ステータスを更新: 行${rowNumber} -> ${status}`);
  return true;
}

// ============================================================================
// 統計情報
// ============================================================================

/**
 * 統計情報を更新
 */
function updateStatistics() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let statsSheet = ss.getSheetByName(CONFIG.STATS_SHEET_NAME);
  
  // 統計情報シートがなければ作成
  if (!statsSheet) {
    statsSheet = ss.insertSheet(CONFIG.STATS_SHEET_NAME);
    
    // ヘッダーを設定
    statsSheet.appendRow(['指標', '値', '最終更新']);
    statsSheet.getRange('A1:C1').setFontWeight('bold').setBackground('#4a86e8').setFontColor('#ffffff');
  }
  
  const mainSheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
  const promptSheet = ss.getSheetByName(CONFIG.PROMPT_SHEET_NAME);
  
  if (!mainSheet) {
    SpreadsheetApp.getUi().alert('エラー: 「実行ログ」シートが見つかりません');
    return;
  }
  
  const mainData = mainSheet.getDataRange().getValues();
  const now = Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'yyyy-MM-dd HH:mm:ss');
  
  // 統計を計算
  const stats = {
    '総実行回数': mainData.length - 1, // ヘッダーを除く
    '成功回数': 0,
    'エラー回数': 0,
    '処理中': 0,
    '平均処理時間': 0,
    '今日の実行回数': 0,
    '今週の実行回数': 0,
    '今月の実行回数': 0
  };
  
  const today = Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'yyyy-MM-dd');
  const thisWeek = getWeekNumber(new Date());
  const thisMonth = Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'yyyy-MM');
  
  let totalProcessingTime = 0;
  let processedCount = 0;
  
  for (let i = 1; i < mainData.length; i++) {
    const status = mainData[i][CONFIG.COL.STATUS - 1];            // K列: ステータス
    const executionTime = mainData[i][CONFIG.COL.EXECUTION_TIME - 1];  // A列: 実行日時
    const processingTime = mainData[i][CONFIG.COL.PROCESSING_TIME - 1]; // J列: 処理時間
    
    // ステータスのカウント
    if (status === '完了') stats['成功回数']++;
    else if (status === 'エラー') stats['エラー回数']++;
    else if (status === '処理中') stats['処理中']++;
    
    // 処理時間の集計
    if (processingTime && typeof processingTime === 'string') {
      const seconds = parseProcessingTime(processingTime);
      if (seconds > 0) {
        totalProcessingTime += seconds;
        processedCount++;
      }
    }
    
    // 日付別の集計
    const execDate = Utilities.formatDate(new Date(executionTime), CONFIG.TIMEZONE, 'yyyy-MM-dd');
    const execWeek = getWeekNumber(new Date(executionTime));
    const execMonth = Utilities.formatDate(new Date(executionTime), CONFIG.TIMEZONE, 'yyyy-MM');
    
    if (execDate === today) stats['今日の実行回数']++;
    if (execWeek === thisWeek) stats['今週の実行回数']++;
    if (execMonth === thisMonth) stats['今月の実行回数']++;
  }
  
  // 平均処理時間を計算
  if (processedCount > 0) {
    const avgSeconds = totalProcessingTime / processedCount;
    stats['平均処理時間'] = formatSeconds(avgSeconds);
  }
  
  // 成功率を追加
  const totalExecuted = stats['成功回数'] + stats['エラー回数'];
  if (totalExecuted > 0) {
    stats['成功率'] = `${(stats['成功回数'] / totalExecuted * 100).toFixed(1)}%`;
  } else {
    stats['成功率'] = '0%';
  }
  
  // 統計情報シートをクリアして更新
  statsSheet.getRange(2, 1, statsSheet.getLastRow(), 3).clearContent();
  
  let row = 2;
  for (const [key, value] of Object.entries(stats)) {
    statsSheet.getRange(row, 1).setValue(key);
    statsSheet.getRange(row, 2).setValue(value);
    statsSheet.getRange(row, 3).setValue(now);
    row++;
  }
  
  // サムネイル統計
  row++;
  const thumbnailCount = mainData.filter((r, i) => i > 0 && r[CONFIG.COL.THUMBNAIL_TEXT - 1]).length;
  statsSheet.getRange(row, 1).setValue('サムネイル生成数');
  statsSheet.getRange(row, 2).setValue(thumbnailCount);
  statsSheet.getRange(row, 3).setValue(now);
  
  // 列幅を自動調整
  statsSheet.autoResizeColumns(1, 3);
  
  SpreadsheetApp.getUi().alert('✅ 統計情報を更新しました');
}

// ============================================================================
// ユーティリティ関数
// ============================================================================

/**
 * 処理時間文字列を秒に変換
 */
function parseProcessingTime(timeStr) {
  // 例: "25分30秒" -> 1530秒
  const minuteMatch = timeStr.match(/(\d+)分/);
  const secondMatch = timeStr.match(/(\d+)秒/);
  
  let seconds = 0;
  if (minuteMatch) seconds += parseInt(minuteMatch[1]) * 60;
  if (secondMatch) seconds += parseInt(secondMatch[1]);
  
  return seconds;
}

/**
 * 秒を時間文字列に変換
 */
function formatSeconds(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}分${secs}秒`;
}

/**
 * 週番号を取得
 */
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// ============================================================================
// データ検証
// ============================================================================

/**
 * データ検証を実行
 */
function validateData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const mainSheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
  
  if (!mainSheet) {
    SpreadsheetApp.getUi().alert('エラー: 「実行ログ」シートが見つかりません');
    return;
  }
  
  const data = mainSheet.getDataRange().getValues();
  const errors = [];
  
  for (let i = 1; i < data.length; i++) {
    const timestamp = data[i][CONFIG.COL.EXECUTION_TIME - 1];
    const title = data[i][CONFIG.COL.TITLE - 1];
    const status = data[i][CONFIG.COL.STATUS - 1];
    
    // 実行日時が空
    if (!timestamp) {
      errors.push(`行${i + 1}: 実行日時が空です`);
    }
    
    // ステータスが不正
    if (!['処理中', '完了', 'エラー'].includes(status)) {
      errors.push(`行${i + 1}: ステータスが不正です (${status})`);
    }
    
    // 完了しているのにタイトルが空
    if (status === '完了' && !title) {
      errors.push(`行${i + 1}: 完了しているのにタイトルが空です`);
    }
  }
  
  if (errors.length === 0) {
    SpreadsheetApp.getUi().alert('✅ データ検証: エラーはありません');
  } else {
    SpreadsheetApp.getUi().alert(`⚠️ ${errors.length}件のエラーが見つかりました:\n\n${errors.join('\n')}`);
  }
}

// ============================================================================
// アーカイブ
// ============================================================================

/**
 * 30日以上前のログをアーカイブ
 */
function archiveOldLogs() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const mainSheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
  
  if (!mainSheet) {
    SpreadsheetApp.getUi().alert('エラー: 「実行ログ」シートが見つかりません');
    return;
  }
  
  const ui = SpreadsheetApp.getUi();
  const result = ui.alert(
    'アーカイブの確認',
    '30日以上前のログをアーカイブシートに移動しますか？',
    ui.ButtonSet.YES_NO
  );
  
  if (result !== ui.Button.YES) return;
  
  // アーカイブシートを取得または作成
  let archiveSheet = ss.getSheetByName('アーカイブ');
  if (!archiveSheet) {
    archiveSheet = ss.insertSheet('アーカイブ');
    // ヘッダーをコピー
    const headers = mainSheet.getRange(1, 1, 1, 11).getValues();
    archiveSheet.getRange(1, 1, 1, 11).setValues(headers);
  }
  
  const data = mainSheet.getDataRange().getValues();
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000));
  
  let archivedCount = 0;
  
  // 下から上に削除（インデックスずれを防ぐ）
  for (let i = data.length - 1; i >= 1; i--) {
    const executionTime = new Date(data[i][1]);
    
    if (executionTime < thirtyDaysAgo) {
      // アーカイブシートに追加
      archiveSheet.appendRow(data[i]);
      // 元のシートから削除
      mainSheet.deleteRow(i + 1);
      archivedCount++;
    }
  }
  
  ui.alert(`✅ ${archivedCount}件のログをアーカイブしました`);
}

// ============================================================================
// Web API（Python側から呼び出すための関数）
// ============================================================================

/**
 * GETリクエスト処理（動作確認用）
 */
function doGet(e) {
  const params = e.parameter;
  const action = params.action;
  
  try {
    if (action === 'test') {
      return ContentService.createTextOutput(
        JSON.stringify({
          success: true, 
          message: 'YouTube AI Podcast API is working!',
          timestamp: new Date().toISOString()
        })
      ).setMimeType(ContentService.MimeType.JSON);
      
    } else if (action === 'get_prompts') {
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const promptSheet = ss.getSheetByName(CONFIG.PROMPT_SHEET_NAME);
      
      if (!promptSheet) {
        return ContentService.createTextOutput(
          JSON.stringify({success: false, error: 'プロンプトシートが見つかりません'})
        ).setMimeType(ContentService.MimeType.JSON);
      }
      
      const infoCollectPrompt = getActivePrompt(promptSheet, 'INFO_COLLECT');
      const scriptGeneratePrompt = getActivePrompt(promptSheet, 'SCRIPT_GENERATE');
      
      return ContentService.createTextOutput(
        JSON.stringify({
          success: true,
          prompts: {
            info_collect: infoCollectPrompt,
            script_generate: scriptGeneratePrompt
          }
        })
      ).setMimeType(ContentService.MimeType.JSON);
      
    } else if (action === 'get_stats') {
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const mainSheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
      
      if (!mainSheet) {
        return ContentService.createTextOutput(
          JSON.stringify({success: false, error: '実行ログシートが見つかりません'})
        ).setMimeType(ContentService.MimeType.JSON);
      }
      
      const data = mainSheet.getDataRange().getValues();
      const stats = {
        total: data.length - 1,
        completed: 0,
        processing: 0,
        error: 0
      };
      
      for (let i = 1; i < data.length; i++) {
        const status = data[i][2];
        if (status === '完了') stats.completed++;
        else if (status === '処理中') stats.processing++;
        else if (status === 'エラー') stats.error++;
      }
      
      return ContentService.createTextOutput(
        JSON.stringify({success: true, stats: stats})
      ).setMimeType(ContentService.MimeType.JSON);
    }
    
    return ContentService.createTextOutput(
      JSON.stringify({
        success: false, 
        error: 'Unknown action',
        available_actions: ['test', 'get_prompts', 'get_stats']
      })
    ).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(
      JSON.stringify({success: false, error: error.toString()})
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * POSTリクエスト処理（データ更新用）
 */
function doPost(e) {
  try {
    const params = JSON.parse(e.postData.contents);
    const action = params.action;
    
    if (action === 'save_metadata') {
      // メタデータを保存（v2.0構造）
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
      
      if (!sheet) {
        return ContentService.createTextOutput(
          JSON.stringify({success: false, error: '実行ログシートが見つかりません'})
        ).setMimeType(ContentService.MimeType.JSON);
      }
      
      // ヘッダーが存在しない場合は作成
      if (sheet.getLastRow() === 0) {
        initializeSheet(sheet);
      }
      
      const now = new Date();
      const timestamp = Utilities.formatDate(now, CONFIG.TIMEZONE, 'yyyy-MM-dd HH:mm:ss');
      
      const metadata = params.metadata || {};
      const comment = params.comment || '';
      const videoPath = params.video_path || '';
      const audioPath = params.audio_path || '';
      const thumbnailPath = params.thumbnail_path || '';
      const processingTime = params.processing_time || '';
      
      // 新しい行を追加
      const newRow = [
        timestamp,                                  // A: 実行日時
        metadata.title || '',                       // B: タイトル
        (metadata.description || '').substring(0, 500), // C: 説明文（500文字まで）
        (metadata.tags || []).join(', '),          // D: タグ
        metadata.thumbnail_text || '',              // E: サムネイルテキスト
        comment,                                    // F: コメント
        videoPath,                                  // G: 動画パス
        audioPath,                                  // H: 音声パス
        thumbnailPath,                              // I: サムネイルパス
        processingTime,                             // J: 処理時間
        '完了',                                     // K: ステータス
        '',                                         // L: 動画URL
        '',                                         // M: 音声URL
        ''                                          // N: サムネイルURL
      ];
      
      sheet.appendRow(newRow);
      const rowNumber = sheet.getLastRow();
      
      // ステータスセルに背景色を設定
      sheet.getRange(rowNumber, CONFIG.COL.STATUS).setBackground('#d9ead3');
      
      Logger.log(`メタデータを保存: 行${rowNumber}`);
      
      return ContentService.createTextOutput(
        JSON.stringify({
          success: true,
          row_number: rowNumber,
          message: 'メタデータを保存しました'
        })
      ).setMimeType(ContentService.MimeType.JSON);
      
    } else if (action === 'create_log') {
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
      
      if (!sheet) {
        return ContentService.createTextOutput(
          JSON.stringify({success: false, error: '実行ログシートが見つかりません'})
        ).setMimeType(ContentService.MimeType.JSON);
      }
      
      // 実行IDを生成
      const now = new Date();
      const dateStr = Utilities.formatDate(now, CONFIG.TIMEZONE, 'yyyyMMdd');
      const lastRow = sheet.getLastRow();
      const sequenceNum = String(lastRow).padStart(3, '0');
      const executionId = `${dateStr}_${sequenceNum}`;
      
      // プロンプトを取得（カスタムプロンプトが指定されている場合はそれを使用）
      let infoCollectPrompt, scriptGeneratePrompt;
      
      if (params.custom_prompts) {
        infoCollectPrompt = params.custom_prompts.info_collect || '';
        scriptGeneratePrompt = params.custom_prompts.script_generate || '';
      } else {
        const promptSheet = ss.getSheetByName(CONFIG.PROMPT_SHEET_NAME);
        infoCollectPrompt = getActivePrompt(promptSheet, 'INFO_COLLECT');
        scriptGeneratePrompt = getActivePrompt(promptSheet, 'SCRIPT_GENERATE');
      }
      
      // 新しい行を追加
      const newRow = [
        executionId,
        Utilities.formatDate(now, CONFIG.TIMEZONE, 'yyyy-MM-dd HH:mm:ss'),
        '処理中',
        infoCollectPrompt,
        '',
        scriptGeneratePrompt,
        '',
        '',
        '',
        '',
        ''
      ];
      
      sheet.appendRow(newRow);
      const lastRowNum = sheet.getLastRow();
      sheet.getRange(lastRowNum, 3).setBackground('#fff4cc');
      
      return ContentService.createTextOutput(
        JSON.stringify({
          success: true, 
          execution_id: executionId,
          prompt_a: infoCollectPrompt,
          prompt_b: scriptGeneratePrompt
        })
      ).setMimeType(ContentService.MimeType.JSON);
      
    } else if (action === 'update_log') {
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = ss.getSheetByName(CONFIG.MAIN_SHEET_NAME);
      
      if (!sheet) {
        return ContentService.createTextOutput(
          JSON.stringify({success: false, error: '実行ログシートが見つかりません'})
        ).setMimeType(ContentService.MimeType.JSON);
      }
      
      const executionId = params.execution_id;
      const data = sheet.getDataRange().getValues();
      
      for (let i = 1; i < data.length; i++) {
        if (data[i][0] === executionId) {
          // 各列を更新
          if (params.status) sheet.getRange(i + 1, 3).setValue(params.status);
          if (params.search_result) sheet.getRange(i + 1, 5).setValue(params.search_result);
          if (params.generated_script) sheet.getRange(i + 1, 7).setValue(params.generated_script);
          if (params.audio_url) sheet.getRange(i + 1, 8).setValue(params.audio_url);
          if (params.video_url) sheet.getRange(i + 1, 9).setValue(params.video_url);
          if (params.processing_time) sheet.getRange(i + 1, 10).setValue(params.processing_time);
          if (params.notes) sheet.getRange(i + 1, 11).setValue(params.notes);
          
          // ステータスに応じて背景色を変更
          if (params.status === '完了') {
            sheet.getRange(i + 1, 3).setBackground('#d9ead3');
          } else if (params.status === 'エラー') {
            sheet.getRange(i + 1, 3).setBackground('#f4cccc');
          }
          
          return ContentService.createTextOutput(
            JSON.stringify({success: true, message: 'ログを更新しました'})
          ).setMimeType(ContentService.MimeType.JSON);
        }
      }
      
      return ContentService.createTextOutput(
        JSON.stringify({success: false, error: '指定された実行IDが見つかりません'})
      ).setMimeType(ContentService.MimeType.JSON);
    }
    
    return ContentService.createTextOutput(
      JSON.stringify({success: false, error: 'Unknown action'})
    ).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(
      JSON.stringify({success: false, error: error.toString()})
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

