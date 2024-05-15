(function(w, $){
    function onReady(){
        // select all existing uploadfield_nodes 
        // without special grappelli blocks :not([id*="__prefix__"])
        var uploadfield_nodes = document.querySelectorAll('.uploadfield_app:not([id*="__prefix__"])');
        var csrftoken = Cookies.get('csrftoken');
        // tmpl for dynamic added field
        var boundTemplate = function(field_name, allowed_title) {
            return `
            <div v-if="preview_exists" class="uploadfield_app__preview" :class="filetype_lower" :style="$options.placeholder_size">
                <div v-if="preview.filetype == 'Image'">
                    <img class="preview" :src="preview.thumbnail" alt="">
                </div>
                <div v-else>
                    <span><a :href="preview.url" target="_blank" class="link">{{ preview.filename }}</a> ({{ preview.filesize }})</span>
                </div>

                <a v-if="field_value" class="uploadfield_app__delete" href="javascript://"  @click="deleteFile"><img src="/static/uploadfield/images/close.svg"></a>
                <a v-if="field_value && preview.filetype == 'Image'" class="uploadfield_app__view" data-fancybox :data-options='fancy_options' :href="preview.url"><img src="/static/uploadfield/images/view.svg"></a>
                <span v-if="field_value && preview.filetype == 'Image'" class="uploadfield_app__size">{{ preview.filesize }}</span>
            </div>

            <div v-show="!field_value" class="uploadfield_app__add-new">
                <div v-show="!uploading" id="${field_name}-add" class="uploadfield_app__images-add" :style="$options.placeholder_size"></div>
                <div v-if="uploading" class="uploadfield_app__images-loading">
                    <span v-text="totalBytes + '%'"></span>
                </div>
            </div>
            <div v-if="valid_extensions" class="uploadfield_app__extentions">${allowed_title}: {{ valid_extensions }}</div>`
        };

        w.uploadfield = {
            apps: [],
            initApp: null
        };
        Dropzone.autoDiscover = false;

        function initApp(app_node) {            
            var field_node = app_node.querySelector('.uploadfield__field');
            var extensions = JSON.parse(field_node.dataset.extensions);
            var thumbnail_name = field_node.dataset.thumbnail;
            var thumbnail_size = JSON.parse(field_node.dataset.thumbnail_size);
            var dropzone_options = JSON.parse(field_node.dataset.dropzoneOptions);
            var field_name = field_node.getAttribute('name');
            var allowed_title = field_node.getAttribute('allowed_title');
            var tmpl = boundTemplate(field_name, allowed_title);
            var add_zone_node;
            var directory = field_node.dataset.directory;
            var dz;
            var dz_tmpl = `<div class="dz-preview dz-file-preview">
              <div class="dz-progress"><span class="dz-upload" data-dz-uploadprogress></span></div>
              <div class="dz-error-message"><span data-dz-errormessage></span></div>
            </div>`;
            // we need to add vue functionality dynamicaly
            // because we need to work also with dynamicaly added nodes.
            // append vue tmpl to widjet
            app_node.querySelector('.uploadfield_app_tmpl').insertAdjacentHTML('afterbegin', tmpl);
            add_zone_node = app_node.querySelector('.uploadfield_app__images-add');
            // add dynamicaly 'v-model' to field node
            field_node.setAttribute('v-model', 'field_value');

            // initial data object
            var data = {
                name: field_node.getAttribute('name'),
                field_value: field_node.value,
                preview: {},
                uploading: false,
                totalBytes: 0
            };

            var app = new Vue({
                el: app_node,
                data: data,
                placeholder_size: {
                    width: thumbnail_size.width + 'px',
                    height: thumbnail_size.height ? thumbnail_size.height + 'px' : thumbnail_size.width + 'px'
                },
                mounted: function(){
                    this.initDropzone();
                    this.getPreview();
                },
                methods: {
                    initDropzone: function() {
                        var dz_options = { 
                            url: "/uploadfield/upload/",
                            headers: {"X-CSRFToken": csrftoken},
                            paramName: 'files',
                            maxFiles: 1,
                            timeout: 0,
                            createImageThumbnails: false,
                            previewTemplate: dz_tmpl
                        };

                        if (dropzone_options) {
                            dz_options = Object.assign({}, dz_options, dropzone_options);
                        }

                        dz = new Dropzone('#' + add_zone_node.id, dz_options);
                        dz.on('totaluploadprogress', function(totalBytes, totalBytesSent){
                            app.totalBytes = parseInt(totalBytes);
                        });
                        dz.on("addedfile", function(file) {
                            app.uploading = true;
                            window.onbeforeunload = () => { return false }
                        });
                        dz.on('success', function(e, data){
                            app.field_value = data.file;
                        });
                        dz.on('queuecomplete', function(){
                            app.uploading = false; 
                            destroyDZ(dz);
                            app.initDropzone();
                            window.onbeforeunload = () => { return }
                        });
                    },
                    deleteFile: function() {
                        app.field_value = "";
                    },
                    getPreview: function() {
                        if ( this.field_value ) {
                            var url = '/uploadfield/preview/?file=' + this.field_value;
                            if (typeof thumbnail_name !== 'undefined') {
                                url += '&thumbnail_name=' + thumbnail_name;
                            }
                            $.getJSON(url, function(data){
                                app.preview = data;
                            });
                        } else {
                            this.preview = {};
                        }
                    }
                },
                computed: {
                    preview_exists: function() {
                        return !$.isEmptyObject(this.preview);
                    },
                    filetype_lower: function() {
                        return app.preview.filetype.toLowerCase();
                    },
                    valid_extensions: function() {
                        return extensions ? extensions.join(', ') : "";
                    },
                    fancy_options: function() {
                        return JSON.stringify({"caption" : this.preview.filename, "src" : this.preview.url})
                    }
                },
                watch: {
                    field_value: function(n, o) {
                        app.getPreview();
                    }
                }
            });
            
            w.uploadfield.apps.push(app);
    
        } // initApp


        function handleNodes(uploadfield_nodes) {
            for (var i = 0; i < uploadfield_nodes.length; i++) {
                initApp(uploadfield_nodes[i]);
            }            
        }
        // first run
        handleNodes(uploadfield_nodes);
        // function visibility
        w.uploadfield.handleNodes = handleNodes;

    } // onReady

    function destroyDZ(dz) {
        dz.off();
        dz.destroy();
    }

    window.addEventListener('DOMContentLoaded', function(event) {
        onReady();
    });

})(window, $ || django.jQuery);

// for admin inlines
if (typeof grp !== 'undefined') {
    // for grappelli inlines
    window.onload = function(){
        var $ = django.jQuery;
        $('.grp-dynamic-form .grp-add-handler').click(function(){
            var new_inline = $(this).closest('.grp-dynamic-form').prev().find('.grp-empty-form').prev();
            var uploadfield_nodes = new_inline[0].querySelectorAll('.uploadfield_app');
            setTimeout(function(){
                window.uploadfield.handleNodes(uploadfield_nodes);    
            }, 200);
        });
    };    
} else if (typeof django !== 'undefined') {
    // for django admin inlines
    window.onload = function(){
        var $ = django.jQuery;
        $('.add-row a').click(function(){
            var new_inline = $(this).closest('.inline-related').find('.empty-form').prev();
            var uploadfield_nodes = new_inline[0].querySelectorAll('.uploadfield_app');
            setTimeout(function(){
                window.uploadfield.handleNodes(uploadfield_nodes);    
            }, 200);
        });
    };    
}
