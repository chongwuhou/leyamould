from localized_blog_links import disable_unpublished_blog_links


def main():
    source = (
        '<article><a class="card" href="/blog/live-guide/">Live guide</a>'
        '<a class="card" href="/blog/future-guide/">Future guide</a>'
        '<a href="/blog/">All guides</a>'
        '<a href="/products/2501/">Product</a>'
        '<a href="https://example.com/blog/external/">External</a>'
        '<a href="https://xuyibottles.com/blog/future-absolute/">Future absolute</a>'
        '</article>'
    )
    published = {"/blog/", "/blog/live-guide/", "/products/2501/"}
    rendered = disable_unpublished_blog_links(source, published)

    assert 'href="/blog/live-guide/"' in rendered
    assert 'href="/blog/future-guide/"' not in rendered
    assert 'data-xuyi-unpublished-route="/blog/future-guide/"' in rendered
    assert 'aria-disabled="true"' in rendered
    assert ">Future guide</a>" in rendered
    assert 'href="/blog/"' in rendered
    assert 'href="/products/2501/"' in rendered
    assert 'href="https://example.com/blog/external/"' in rendered
    assert 'href="https://xuyibottles.com/blog/future-absolute/"' not in rendered
    assert 'data-xuyi-unpublished-route="/blog/future-absolute/"' in rendered
    assert disable_unpublished_blog_links(rendered, published) == rendered
    print("LOCALIZED_BLOG_UNPUBLISHED_LINK_TESTS_PASSED")


if __name__ == "__main__":
    main()
