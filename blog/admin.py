from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Article, Comment

# Admin Site Header & Titles
admin.site.site_header = "POSTIFY — The Living Journal"
admin.site.site_title = "Postify Administration"
admin.site.index_title = "Publication Archives & Editorial Administration"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title_preview',
        'owner_badge',
        'category_badges',
        'engagement_metrics',
        'created_formatted',
    )
    list_filter = ('category', 'created', 'owner')
    search_fields = ('title', 'desc', 'content', 'owner__username')
    date_hierarchy = 'created'
    ordering = ('-created',)
    filter_horizontal = ('bookmarks', 'upvote', 'downvote')
    readonly_fields = ('created',)

    fieldsets = (
        ("Editorial Core", {
            "fields": ("title", "desc", "owner", "created"),
            "description": "Primary publication metadata and authorship."
        }),
        ("Manuscript & Media", {
            "fields": ("content", "artImage", "category"),
            "description": "Article prose formatted with Markdown, topic categories, and plate cover."
        }),
        ("Reader Engagement", {
            "fields": ("upvote", "downvote", "bookmarks"),
            "classes": ("collapse",),
            "description": "Registered reader votes and saved reading list records."
        }),
    )

    def title_preview(self, obj):
        return format_html(
            '<div style="font-weight: 600; font-family: Newsreader, Georgia, serif; font-size: 1.05rem; color: #181716;">'
            '{}'
            '<div style="font-weight: 400; font-family: system-ui, sans-serif; font-size: 0.78rem; color: #6b665e; margin-top: 2px;">{}</div>'
            '</div>',
            obj.title,
            obj.desc[:90] + ("..." if len(obj.desc) > 90 else "")
        )
    title_preview.short_description = "Dispatch Title"

    def owner_badge(self, obj):
        return format_html(
            '<span style="display: inline-flex; align-items: center; gap: 6px; font-weight: 600; color: #181716;">'
            '<span style="width: 20px; height: 20px; border-radius: 50%; background: #cf3c22; color: #fff; font-size: 0.65rem; display: inline-flex; align-items: center; justify-content: center;">{}</span>'
            '@{}'
            '</span>',
            obj.owner.username[:1].upper(),
            obj.owner.username
        )
    owner_badge.short_description = "Author"

    def category_badges(self, obj):
        badges = []
        for cat in obj.category:
            badges.append(
                format_html(
                    '<span style="background: #fbf8f3; border: 1px solid #d5cbbe; color: #524e47; '
                    'padding: 2px 8px; border-radius: 9999px; font-size: 0.72rem; font-family: monospace; text-transform: uppercase;">'
                    '{}</span>',
                    cat
                )
            )
        if not badges:
            return "—"
        return mark_safe(" ".join(badges))
    category_badges.short_description = "Curated Topics"

    def engagement_metrics(self, obj):
        return format_html(
            '<span style="font-family: monospace; font-size: 0.78rem; color: #524e47;">'
            '<span style="color: #cf3c22; font-weight: 600;">▲ {}</span> votes &nbsp;·&nbsp; '
            '<span style="color: #181716;">★ {}</span> saved'
            '</span>',
            obj.upvote.count(),
            obj.bookmarks.count()
        )
    engagement_metrics.short_description = "Reader Metrics"

    def created_formatted(self, obj):
        return format_html(
            '<span style="font-family: monospace; font-size: 0.76rem; color: #6b665e;">{}</span>',
            obj.created.strftime("%b %d, %Y · %I:%M %p")
        )
    created_formatted.short_description = "Inscribed At"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('owner_badge', 'article_link', 'content_snippet', 'created_formatted')
    list_filter = ('created', 'owner')
    search_fields = ('content', 'owner__username', 'article__title')
    date_hierarchy = 'created'
    readonly_fields = ('created',)

    def owner_badge(self, obj):
        return format_html(
            '<span style="font-weight: 600; color: #181716;">@{}</span>',
            obj.owner.username
        )
    owner_badge.short_description = "Reader"

    def article_link(self, obj):
        return format_html(
            '<span style="font-family: Newsreader, Georgia, serif; font-weight: 500; font-size: 0.95rem; color: #181716;">{}</span>',
            obj.article.title[:50] + ("..." if len(obj.article.title) > 50 else "")
        )
    article_link.short_description = "On Dispatch"

    def content_snippet(self, obj):
        return format_html(
            '<span style="font-size: 0.84rem; color: #524e47;">{}</span>',
            obj.content[:80] + ("..." if len(obj.content) > 80 else "")
        )
    content_snippet.short_description = "Commentary"

    def created_formatted(self, obj):
        return format_html(
            '<span style="font-family: monospace; font-size: 0.76rem; color: #6b665e;">{}</span>',
            obj.created.strftime("%b %d, %Y · %I:%M %p")
        )
    created_formatted.short_description = "Submitted At"
