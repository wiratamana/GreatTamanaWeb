/* ==========================================================================
   apptools.js  -  the tool inventory of GreatTamanaApp (counted from the source, 2026-11-13).
   173 tools = 167 [ToolInfo] in GTA.Tools + 6 UI-only tools in GTA.App.
   Names are code identifiers, so they are not translated.
   Category description: i18n/<lang>/app.js  ->  app.tools.<id>
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  GTW.appTools = [
    { id: "io", n: 26, names: "append_to_file browse_dir browse_dir_recursive compare_files copy_file create_dir deduplicate_lines delete_dir delete_file detect_encoding edit_line find_files get_dir_size get_file_info get_file_line_count insert_line move_file read_file read_file_base64 read_line remove_line replace_in_file search_in_dir search_line sort_lines write_file" },
    { id: "git", n: 41, names: "git_add git_branch_create git_branch_delete git_branch_list git_clean git_clone git_commit git_config git_create_pull_request git_create_remote_repository git_diff git_fetch git_init git_list_issues git_log git_log_oneline git_merge git_mv git_post_issue_comment git_pull git_push git_read_issue git_read_issue_comments git_rebase git_reset_hard git_reset_soft git_restore git_restore_staged git_revert git_rm git_set_issue_state git_show git_stash git_stash_apply git_stash_drop git_stash_list git_stash_pop git_status git_switch git_switch_create git_tag" },
    { id: "pptx", n: 20, names: "pptx_read pptx_new_pptx pptx_new_slide pptx_delete_slide pptx_move_slide pptx_apply_batch pptx_text_box pptx_bullet_list pptx_image pptx_table pptx_chart pptx_set_rect pptx_shape_rectangle pptx_shape_rounded_rectangle pptx_shape_diamond pptx_shape_arrow pptx_shape_line pptx_shape_line_arrow pptx_shape_connector pptx_shape_elbow_connector" },
    { id: "xlsx", n: 11, names: "xlsx_create_sheets xlsx_duplicate_sheets xlsx_fill_formula xlsx_fill_range xlsx_merge_cells xlsx_query_sheets xlsx_read_cells xlsx_read_range xlsx_read_sheet xlsx_rename_sheets xlsx_set_cell_values" },
    { id: "ext", n: 13, names: "run_shell gcc cmake inline_python run_app_background stop_app_background http_request gte_send_request load_image zip_files extract_zip get_available_tools load_tools" },
    { id: "dotnet", n: 5, names: "dotnet_build dotnet_build_and_run dotnet_create_console_project dotnet_get_all_cs_files dotnet_run" },
    { id: "ui", n: 8, names: "launch_avalonia check_avalonia_status close_avalonia take_screenshot avalonia_send_message avalonia_busy avalonia_get_agent avalonia_set_agent" },
    { id: "sub", n: 6, names: "dispatch_sub_agent ask_questions delegate_task task_status restart_task forward_report" },
    { id: "ent", n: 40, names: "box_* jira_* teams_* outlook_fetch_mail ibmcloud_*" },
    { id: "misc", n: 3, names: "encyclopedia_read encyclopedia_write bug_report" }
  ];
})();
