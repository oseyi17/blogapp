from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    
    #List (sort) posts with specific tags
    tag=None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    
    #pagination
    paginator = Paginator(object_list, 5) #5 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page':page,'posts':posts,'tag':tag})

def post_detail(request, year, month, day, post ):
    post = get_object_or_404(Post, slug=post,
                                status='published',
                                publish__year = year,
                                publish__month=month,
                                publish__day=day)
    
    #Retrieve all active commets for a post
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post=post #assign current post to the comment just created
            new_comment.save() #save comment to database
    else:
        comment_form = CommentForm()
    
    return render(request, 'blog/post/detail.html', 
                            {'post':post,
                            'comments':comments,
                            'new_comment':new_comment,
                            'comment_form':comment_form})

#share post by email
def post_shared(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read" f"{post.title}"
            message = f"Read{post.title} at {post_url}\n\n" f"{cd['name']}'\s comments:{cd['comments']}" 
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent} )